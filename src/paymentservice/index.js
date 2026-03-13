/*
 * PaymentService - Cloud-Agnostic Version
 *
 * The original index.js already had GCP profiler removed.
 * This version is cleaned up and confirmed cloud-agnostic:
 *   - No @google-cloud/profiler
 *   - No @google-cloud/trace-agent
 *   - OpenTelemetry OTLP tracing kept (works with any backend)
 *   - All config via environment variables
 */

'use strict';

const logger = require('./logger');
logger.info("PaymentService starting in cloud-agnostic mode.");

if (process.env.ENABLE_TRACING === "1") {
  logger.info("Tracing enabled.");

  const { resourceFromAttributes } = require('@opentelemetry/resources');
  const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');
  const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');
  const { registerInstrumentations } = require('@opentelemetry/instrumentation');
  const opentelemetry = require('@opentelemetry/sdk-node');
  const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');

  const collectorUrl = process.env.COLLECTOR_SERVICE_ADDR;
  const traceExporter = new OTLPTraceExporter({ url: collectorUrl });

  const sdk = new opentelemetry.NodeSDK({
    resource: resourceFromAttributes({
      [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'paymentservice',
    }),
    traceExporter,
  });

  registerInstrumentations({
    instrumentations: [new GrpcInstrumentation()]
  });

  sdk.start();
} else {
  logger.info("Tracing disabled. Set ENABLE_TRACING=1 and COLLECTOR_SERVICE_ADDR to enable.");
}

const path = require('path');
const HipsterShopServer = require('./server');

const PORT = process.env['PORT'] || '50051';
const PROTO_PATH = path.join(__dirname, '/proto/');

const server = new HipsterShopServer(PROTO_PATH, PORT);
server.listen();
