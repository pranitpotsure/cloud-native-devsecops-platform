#!/usr/bin/python
#
# EmailService - Production Email via SendGrid (Free tier: 100 emails/day)
#
# HOW TO GET YOUR FREE SENDGRID API KEY:
#   1. Go to https://signup.sendgrid.com  (free, no credit card)
#   2. Verify your email
#   3. Go to Settings → API Keys → Create API Key
#   4. Choose "Restricted Access" → enable "Mail Send"
#   5. Copy the key → set EMAIL_PROVIDER=sendgrid in docker-compose.yml
#      and SENDGRID_API_KEY=SG.xxxx
#
# ENV VARS:
#   EMAIL_PROVIDER       = sendgrid | smtp | dummy (default: dummy)
#   SENDGRID_API_KEY     = SG.xxxxxxxxxxxx
#   EMAIL_FROM_ADDRESS   = your-verified@email.com  (must be verified in SendGrid)
#   EMAIL_FROM_NAME      = Online Boutique (optional)
#
#   For SMTP (Gmail, etc.):
#   SMTP_HOST            = smtp.gmail.com
#   SMTP_PORT            = 587
#   SMTP_USER            = your@gmail.com
#   SMTP_PASSWORD        = your-app-password  (Gmail: use App Password, not real password)
#   EMAIL_FROM_ADDRESS   = your@gmail.com

from concurrent import futures
import os
import sys
import time
import grpc
import traceback
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateError

import demo_pb2
import demo_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from opentelemetry import trace

from logger import getJSONLogger
logger = getJSONLogger('emailservice-server')

# Load email confirmation template
env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('confirmation.html')

# ─────────────────────────────────────────────
# Email Senders
# ─────────────────────────────────────────────

def send_via_sendgrid(to_email, subject, html_content):
    """Send email using SendGrid API (free tier: 100/day, no credit card)"""
    import urllib.request
    import urllib.error
    import json

    api_key = os.environ.get('SENDGRID_API_KEY', '')
    from_email = os.environ.get('EMAIL_FROM_ADDRESS', '')
    from_name = os.environ.get('EMAIL_FROM_NAME', 'Online Boutique')

    if not api_key:
        raise ValueError("SENDGRID_API_KEY environment variable is not set")
    if not from_email:
        raise ValueError("EMAIL_FROM_ADDRESS environment variable is not set")

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": from_name},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}]
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            logger.info(f"SendGrid: email sent to {to_email}, status={response.status}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"SendGrid error {e.code}: {body}")


def send_via_smtp(to_email, subject, html_content):
    """Send email using SMTP (works with Gmail, Outlook, any SMTP server)"""
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    from_email = os.environ.get('EMAIL_FROM_ADDRESS', smtp_user)
    from_name = os.environ.get('EMAIL_FROM_NAME', 'Online Boutique')

    if not smtp_user or not smtp_password:
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be set")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{from_name} <{from_email}>"
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())
        logger.info(f"SMTP: email sent to {to_email} via {smtp_host}:{smtp_port}")


def send_email(to_email, subject, html_content):
    """Route to correct email provider based on EMAIL_PROVIDER env var"""
    provider = os.environ.get('EMAIL_PROVIDER', 'dummy').lower()

    if provider == 'sendgrid':
        send_via_sendgrid(to_email, subject, html_content)
    elif provider == 'smtp':
        send_via_smtp(to_email, subject, html_content)
    else:
        # Dummy mode - just log (default, safe for dev)
        logger.info(f"[DUMMY] Email to: {to_email} | Subject: {subject}")
        logger.info(f"[DUMMY] Set EMAIL_PROVIDER=sendgrid or smtp to send real emails")


# ─────────────────────────────────────────────
# gRPC Service
# ─────────────────────────────────────────────

class EmailService(demo_pb2_grpc.EmailServiceServicer):

    def SendOrderConfirmation(self, request, context):
        email = request.email
        order = request.order

        try:
            html_body = template.render(order=order)
        except TemplateError as err:
            context.set_details("Failed to render email template.")
            logger.error(f"Template error: {err}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return demo_pb2.Empty()

        order_id = getattr(order, 'order_id', 'N/A')
        subject = f"Your Online Boutique Order Confirmation #{order_id}"

        try:
            send_email(email, subject, html_body)
            logger.info(f"Order confirmation sent to: {email} for order: {order_id}")
        except Exception as e:
            # Log error but don't fail the order - email is non-critical
            logger.error(f"Failed to send email to {email}: {str(e)}")
            logger.error(traceback.format_exc())
            # Don't return error to caller - order was already placed successfully

        return demo_pb2.Empty()

    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)


def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = EmailService()

    demo_pb2_grpc.add_EmailServiceServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)

    port = os.environ.get('PORT', "8080")
    provider = os.environ.get('EMAIL_PROVIDER', 'dummy')
    logger.info(f"EmailService starting on port {port} | provider={provider}")
    server.add_insecure_port('[::]:' + port)
    server.start()

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logger.info('Starting EmailService (production-ready)')

    # OpenTelemetry Tracing - imports inside try/except so startup never crashes
    try:
        from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        if os.environ.get("ENABLE_TRACING") == "1":
            otel_endpoint = os.getenv("COLLECTOR_SERVICE_ADDR", "localhost:4317")
            logger.info(f"Tracing enabled. Exporting to: {otel_endpoint}")
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
                )
            )
        else:
            logger.info("Tracing disabled.")

        grpc_server_instrumentor = GrpcInstrumentorServer()
        grpc_server_instrumentor.instrument()

    except Exception as e:
        logger.warning(f"Tracing setup failed (non-fatal): {traceback.format_exc()}")

    start()