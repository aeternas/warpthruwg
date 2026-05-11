FROM alexishw/amneziawg-web-ui:master

COPY patches/apply_ipv6_support.py /usr/local/bin/apply_ipv6_support.py
RUN python3 /usr/local/bin/apply_ipv6_support.py /app/web-ui/app.py
