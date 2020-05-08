# http-service-with-rate-limiter
HTTP-сервис, способный ограничивать количество запросов (rate limit) из одной подсети IPv4. Если ограничения отсутствуют, то нужно выдавать одинаковый статический контент.

запускать с параметрами prefix_subnet delay limit
Например:
--prefix_subnet=24 --delay=120 --limit="2 per 10 second"


#curl -u abc:abc -i -X POST -H "Content-Type: application/json" -d "{\"subnet\":\"127.0.0.0\"}" http://127.0.0.1:5000/white_list_subnet
#curl -i -H "Content-Type: application/json" -X POST -d "{\"username\":\"abc\", \"password\":\"abc\"}" 127.0.0.1:5000/new_user
