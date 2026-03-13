/*
 * Copyright 2018, Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package hipstershop;

import com.google.common.collect.ImmutableListMultimap;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Iterables;
import hipstershop.Demo.Ad;
import hipstershop.Demo.AdRequest;
import hipstershop.Demo.AdResponse;
import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.StatusRuntimeException;
import io.grpc.health.v1.HealthCheckResponse.ServingStatus;
import io.grpc.services.*;
import io.grpc.stub.StreamObserver;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

/**
 * AdService - Cloud-Agnostic Refactored Version
 *
 * Changes from original GCP version:
 * - Removed Google Cloud Profiler (cprof agent) integration
 * - Removed Stackdriver tracing/stats references
 * - Removed GCP-specific OpenTelemetry exporters
 * - initStats() and initTracing() now respect DISABLE_STATS / DISABLE_TRACING env vars
 *   and log clearly; no GCP calls are made
 * - All configuration via environment variables (PORT, DISABLE_STATS, DISABLE_TRACING)
 * - Logging goes to stdout only (log4j2 configured for plain JSON, no Stackdriver keys)
 */
public final class AdService {

  private static final Logger logger = LogManager.getLogger(AdService.class);

  @SuppressWarnings("FieldCanBeLocal")
  private static int MAX_ADS_TO_SERVE = 2;

  private Server server;
  private HealthStatusManager healthMgr;

  private static final AdService service = new AdService();

  private void start() throws IOException {
    // Read port from environment variable; default to 9555
    int port = Integer.parseInt(System.getenv().getOrDefault("PORT", "9555"));
    healthMgr = new HealthStatusManager();

    server =
        ServerBuilder.forPort(port)
            .addService(new AdServiceImpl())
            .addService(healthMgr.getHealthService())
            .build()
            .start();

    logger.info("Ad Service started, listening on port {}", port);

    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
                  System.err.println("*** shutting down gRPC ads server since JVM is shutting down");
                  AdService.this.stop();
                  System.err.println("*** server shut down");
                }));

    healthMgr.setStatus("", ServingStatus.SERVING);
  }

  private void stop() {
    if (server != null) {
      healthMgr.clearStatus("");
      server.shutdown();
    }
  }

  private static class AdServiceImpl extends hipstershop.AdServiceGrpc.AdServiceImplBase {

    /**
     * Retrieves ads based on context provided in the request {@code AdRequest}.
     *
     * @param req the request containing context.
     * @param responseObserver the stream observer which gets notified with the value of {@code
     *     AdResponse}
     */
    @Override
    public void getAds(AdRequest req, StreamObserver<AdResponse> responseObserver) {
      AdService service = AdService.getInstance();
      try {
        List<Ad> allAds = new ArrayList<>();
        logger.info("Received ad request (context_words={})", req.getContextKeysList());

        if (req.getContextKeysCount() > 0) {
          for (int i = 0; i < req.getContextKeysCount(); i++) {
            Collection<Ad> ads = service.getAdsByCategory(req.getContextKeys(i));
            allAds.addAll(ads);
          }
        } else {
          allAds = service.getRandomAds();
        }

        if (allAds.isEmpty()) {
          // Serve random ads as fallback
          allAds = service.getRandomAds();
        }

        AdResponse reply = AdResponse.newBuilder().addAllAds(allAds).build();
        responseObserver.onNext(reply);
        responseObserver.onCompleted();
      } catch (StatusRuntimeException e) {
        logger.log(Level.WARN, "GetAds failed with status {}", e.getStatus());
        responseObserver.onError(e);
      }
    }
  }

  private static final ImmutableListMultimap<String, Ad> adsMap = createAdsMap();

  private Collection<Ad> getAdsByCategory(String category) {
    return adsMap.get(category);
  }

  private static final Random random = new Random();

  private List<Ad> getRandomAds() {
    List<Ad> ads = new ArrayList<>(MAX_ADS_TO_SERVE);
    Collection<Ad> allAds = adsMap.values();
    for (int i = 0; i < MAX_ADS_TO_SERVE; i++) {
      ads.add(Iterables.get(allAds, random.nextInt(allAds.size())));
    }
    return ads;
  }

  private static AdService getInstance() {
    return service;
  }

  /** Await termination on the main thread since the grpc library uses daemon threads. */
  private void blockUntilShutdown() throws InterruptedException {
    if (server != null) {
      server.awaitTermination();
    }
  }

  private static ImmutableListMultimap<String, Ad> createAdsMap() {
    Ad hairdryer =
        Ad.newBuilder()
            .setRedirectUrl("/product/2ZYFJ3GM2N")
            .setText("Hairdryer for sale. 50% off.")
            .build();
    Ad tankTop =
        Ad.newBuilder()
            .setRedirectUrl("/product/66VCHSJNUP")
            .setText("Tank top for sale. 20% off.")
            .build();
    Ad candleHolder =
        Ad.newBuilder()
            .setRedirectUrl("/product/0PUK6V6EV0")
            .setText("Candle holder for sale. 30% off.")
            .build();
    Ad bambooGlassJar =
        Ad.newBuilder()
            .setRedirectUrl("/product/9SIQT8TOJO")
            .setText("Bamboo glass jar for sale. 10% off.")
            .build();
    Ad watch =
        Ad.newBuilder()
            .setRedirectUrl("/product/1YMWWN1N4O")
            .setText("Watch for sale. Buy one, get second kit for free")
            .build();
    Ad mug =
        Ad.newBuilder()
            .setRedirectUrl("/product/6E92ZMYYFZ")
            .setText("Mug for sale. Buy two, get third one for free")
            .build();
    Ad loafers =
        Ad.newBuilder()
            .setRedirectUrl("/product/L9ECAV7KIM")
            .setText("Loafers for sale. Buy one, get second one for free")
            .build();
    return ImmutableListMultimap.<String, Ad>builder()
        .putAll("clothing", tankTop)
        .putAll("accessories", watch)
        .putAll("footwear", loafers)
        .putAll("hair", hairdryer)
        .putAll("decor", candleHolder)
        .putAll("kitchen", bambooGlassJar, mug)
        .build();
  }

  /**
   * Initializes stats/metrics.
   *
   * REFACTORED: Removed Stackdriver/GCP stats exporter.
   * To enable metrics on AWS, set ENABLE_STATS=true and integrate
   * OpenTelemetry with an OTLP exporter (e.g., AWS X-Ray or Prometheus).
   * By default stats are disabled to keep the service dependency-free.
   */
  private static void initStats() {
    if (System.getenv("DISABLE_STATS") != null) {
      logger.info("Stats disabled via DISABLE_STATS env var.");
      return;
    }
    // Stats are opt-in. Set ENABLE_STATS env var and wire up your preferred
    // OpenTelemetry exporter (OTLP, Prometheus, AWS CloudWatch, etc.)
    logger.info("Stats collection is not configured. Set DISABLE_STATS=true to suppress this message.");
    logger.info("To enable metrics: integrate OpenTelemetry SDK with your preferred exporter.");
  }

  /**
   * Initializes distributed tracing.
   *
   * REFACTORED: Removed Stackdriver/GCP tracing exporter.
   * To enable tracing on AWS, set ENABLE_TRACING=true and configure
   * the OpenTelemetry OTLP exporter pointing to AWS X-Ray or Jaeger.
   * By default tracing is disabled.
   */
  private static void initTracing() {
    if (System.getenv("DISABLE_TRACING") != null) {
      logger.info("Tracing disabled via DISABLE_TRACING env var.");
      return;
    }
    // Tracing is opt-in. Configure OTEL_EXPORTER_OTLP_ENDPOINT env var
    // to point to your tracing backend (Jaeger, AWS X-Ray ADOT collector, etc.)
    logger.info("Tracing is not configured. Set DISABLE_TRACING=true to suppress this message.");
    logger.info("To enable tracing: set OTEL_EXPORTER_OTLP_ENDPOINT and integrate OpenTelemetry SDK.");
  }

  /** Main launches the server from the command line. */
  public static void main(String[] args) throws IOException, InterruptedException {

    new Thread(
            () -> {
              initStats();
              initTracing();
            })
        .start();

    logger.info("AdService starting.");
    final AdService service = AdService.getInstance();
    service.start();
    service.blockUntilShutdown();
  }
}
