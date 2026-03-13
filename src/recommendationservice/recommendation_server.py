#!/usr/bin/python
#
# RecommendationService - Cloud-Agnostic Refactored Version
#
# CHANGES:
#   - Removed googlecloudprofiler (GCP Cloud Profiler)
#   - Removed initStackdriverProfiling() function
#   - Removed google.auth.exceptions import
#   - Removed GCP_PROJECT_ID env var dependency
#   - OpenTelemetry tracing kept (OTLP, cloud-agnostic)
#   - All config via environment variables

import os
import random
import time
import traceback
from concurrent import futures

import grpc

import demo_pb2
import demo_pb2_grpc
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc

from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorClient, GrpcInstrumentorServer
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from logger import getJSONLogger
logger = getJSONLogger('recommendationservice-server')


class RecommendationService(demo_pb2_grpc.RecommendationServiceServicer):
    def ListRecommendations(self, request, context):
        max_responses = 5
        # Fetch list of products from product catalog stub
        cat_response = product_catalog_stub.ListProducts(demo_pb2.Empty())
        product_ids = [x.id for x in cat_response.products]
        filtered_products = list(set(product_ids) - set(request.product_ids))
        num_products = len(filtered_products)
        num_return = min(max_responses, num_products)
        # Sample list of indices to return
        indices = random.sample(range(num_products), num_return)
        prod_list = [filtered_products[i] for i in indices]
        logger.info(f"[Recv ListRecommendations] product_ids={prod_list}")
        response = demo_pb2.ListRecommendationsResponse()
        response.product_ids.extend(prod_list)
        return response

    def Check(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        return health_pb2.HealthCheckResponse(
            status=health_pb2.HealthCheckResponse.UNIMPLEMENTED)


if __name__ == "__main__":
    logger.info("initializing recommendationservice")

    # GCP Profiler removed. For AWS: use AWS CodeGuru Profiler (optional).
    logger.info("GCP Profiler disabled. Running in cloud-agnostic mode.")

    # OpenTelemetry Tracing (optional, works with any OTLP backend)
    try:
        grpc_client_instrumentor = GrpcInstrumentorClient()
        grpc_client_instrumentor.instrument()
        grpc_server_instrumentor = GrpcInstrumentorServer()
        grpc_server_instrumentor.instrument()

        if os.environ.get("ENABLE_TRACING") == "1":
            otel_endpoint = os.getenv("COLLECTOR_SERVICE_ADDR", "localhost:4317")
            logger.info(f"Tracing enabled. Exporting to: {otel_endpoint}")
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(
                        endpoint=otel_endpoint,
                        insecure=True
                    )
                )
            )
        else:
            logger.info("Tracing disabled. Set ENABLE_TRACING=1 to enable.")

    except Exception as e:
        logger.warning(f"Tracing setup failed: {traceback.format_exc()}, continuing without tracing.")

    port = os.environ.get('PORT', "8080")
    catalog_addr = os.environ.get('PRODUCT_CATALOG_SERVICE_ADDR', '')
    if catalog_addr == "":
        raise Exception('PRODUCT_CATALOG_SERVICE_ADDR environment variable not set')

    logger.info(f"product catalog address: {catalog_addr}")
    channel = grpc.insecure_channel(catalog_addr)
    product_catalog_stub = demo_pb2_grpc.ProductCatalogServiceStub(channel)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = RecommendationService()
    demo_pb2_grpc.add_RecommendationServiceServicer_to_server(service, server)
    health_pb2_grpc.add_HealthServicer_to_server(service, server)

    logger.info(f"listening on port: {port}")
    server.add_insecure_port('[::]:' + port)
    server.start()

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)
