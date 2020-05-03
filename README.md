# http-service-with-rate-limiter
HTTP-сервис, способный ограничивать количество запросов (rate limit) из одной подсети IPv4. Если ограничения отсутствуют, то нужно выдавать одинаковый статический контент.

запускать с параметрами prefix_subnet delay limit
Например:
--prefix_subnet=24 --delay=120 --limit="2 per 10 second"