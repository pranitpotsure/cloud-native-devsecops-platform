/*
 * CurrencyService - Cloud-Agnostic Refactored Version
 *
 * CHANGES:
 *   - Removed @google-cloud/profiler entirely
 *   - Removed @google-cloud/trace-agent (GCP-specific)
 *   - OpenTelemetry tracing kept (OTLP exporter, works with any backend)
 *   - All config via environment variables
 *   - Logging to stdout via pino (JSON format)
 */

'use strict';

const pino = require('pino');
const logger = pino({
  name: 'currencyservice-server',
  messageKey: 'message',
  formatters: {
    level(logLevelString) {
      return { severity: logLevelString };
    }
  }
});

// GCP Profiler removed. For AWS: use AWS CodeGuru Profiler (optional).
logger.info("GCP Profiler removed. Running in cloud-agnostic mode.");

// OpenTelemetry gRPC instrumentation for trace propagation
const { GrpcInstrumentation } = require('@opentelemetry/instrumentation-grpc');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');

registerInstrumentations({
  instrumentations: [new GrpcInstrumentation()]
});

if (process.env.ENABLE_TRACING === "1") {
  logger.info("Tracing enabled.");

  const { resourceFromAttributes } = require('@opentelemetry/resources');
  const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');
  const opentelemetry = require('@opentelemetry/sdk-node');
  const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');

  const collectorUrl = process.env.COLLECTOR_SERVICE_ADDR;
  const traceExporter = new OTLPTraceExporter({ url: collectorUrl });
  const sdk = new opentelemetry.NodeSDK({
    resource: resourceFromAttributes({
      [ATTR_SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'currencyservice',
    }),
    traceExporter,
  });
  sdk.start();
} else {
  logger.info("Tracing disabled. Set ENABLE_TRACING=1 and COLLECTOR_SERVICE_ADDR to enable.");
}

const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const MAIN_PROTO_PATH = path.join(__dirname, './proto/demo.proto');
const HEALTH_PROTO_PATH = path.join(__dirname, './proto/grpc/health/v1/health.proto');

const PORT = process.env.PORT || '7000';

const shopProto = _loadProto(MAIN_PROTO_PATH).hipstershop;
const healthProto = _loadProto(HEALTH_PROTO_PATH).grpc.health.v1;

function _loadProto(path) {
  const packageDefinition = protoLoader.loadSync(path, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
  });
  return grpc.loadPackageDefinition(packageDefinition);
}

function _getCurrencyData(callback) {
  const data = require('./data/currency_conversion.json');
  callback(data);
}

function _carry(amount) {
  const fractionSize = Math.pow(10, 9);
  amount.nanos += (amount.units % 1) * fractionSize;
  amount.units = Math.floor(amount.units) + Math.floor(amount.nanos / fractionSize);
  amount.nanos = amount.nanos % fractionSize;
  return amount;
}

function getSupportedCurrencies(call, callback) {
  logger.info('Getting supported currencies...');
  _getCurrencyData((data) => {
    callback(null, { currency_codes: Object.keys(data) });
  });
}

function convert(call, callback) {
  try {
    _getCurrencyData((data) => {
      const request = call.request;
      const from = request.from;
      const euros = _carry({
        units: from.units / data[from.currency_code],
        nanos: from.nanos / data[from.currency_code]
      });
      euros.nanos = Math.round(euros.nanos);
      const result = _carry({
        units: euros.units * data[request.to_code],
        nanos: euros.nanos * data[request.to_code]
      });
      result.units = Math.floor(result.units);
      result.nanos = Math.floor(result.nanos);
      result.currency_code = request.to_code;
      logger.info('conversion request successful');
      callback(null, result);
    });
  } catch (err) {
    logger.error(`conversion request failed: ${err}`);
    callback(err.message);
  }
}

function check(call, callback) {
  callback(null, { status: 'SERVING' });
}

function main() {
  logger.info(`Starting gRPC server on port ${PORT}...`);
  const server = new grpc.Server();
  server.addService(shopProto.CurrencyService.service, { getSupportedCurrencies, convert });
  server.addService(healthProto.Health.service, { check });

  server.bindAsync(
    `[::]:${PORT}`,
    grpc.ServerCredentials.createInsecure(),
    function() {
      logger.info(`CurrencyService gRPC server started on port ${PORT}`);
      server.start();
    }
  );
}

main();
