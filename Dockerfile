FROM alpine:latest

COPY env /env
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]