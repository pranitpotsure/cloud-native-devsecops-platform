// Refactored: Cloud-Agnostic CartService
// CHANGES:
//   - Removed AlloyDBCartStore (GCP AlloyDB + Secret Manager dependency)
//   - Removed SpannerCartStore (GCP Spanner dependency)
//   - Kept RedisCartStore (works with any Redis: ElastiCache, Redis OSS, etc.)
//   - Kept in-memory fallback when REDIS_ADDR is not set
//   - All config via environment variables only

using System;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using cartservice.cartstore;
using cartservice.services;
using Microsoft.Extensions.Caching.StackExchangeRedis;

namespace cartservice
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        public void ConfigureServices(IServiceCollection services)
        {
            string redisAddress = Configuration["REDIS_ADDR"];

            if (!string.IsNullOrEmpty(redisAddress))
            {
                Console.WriteLine($"Using Redis cart store at {redisAddress}");
                services.AddStackExchangeRedisCache(options =>
                {
                    options.Configuration = redisAddress;
                });
                services.AddSingleton<ICartStore, RedisCartStore>();
            }
            else
            {
                // Fallback: in-memory distributed cache — suitable for local dev / single-node
                // For production on AWS: set REDIS_ADDR to your ElastiCache endpoint
                Console.WriteLine("REDIS_ADDR not set. Using in-memory cart store (not suitable for multi-replica deployments).");
                services.AddDistributedMemoryCache();
                services.AddSingleton<ICartStore, RedisCartStore>();
            }

            services.AddGrpc();
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            app.UseRouting();
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapGrpcService<CartService>();
                endpoints.MapGrpcService<cartservice.services.HealthCheckService>();
                endpoints.MapGet("/", async context =>
                {
                    await context.Response.WriteAsync(
                        "Communication with gRPC endpoints must be made through a gRPC client.");
                });
            });
        }
    }
}
