```bash
$ docker exec -it with_dumb_init ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   2064   756 ?        Ss   05:33   0:00 dumb-init -- py
root         7  0.2  0.1  13020 10948 pts/0    Ss+  05:33   0:00 python app.py
root         8  0.0  0.0   8764  6432 pts/0    S+   05:33   0:00 python -c impor
root         9 66.6  0.0   8432  3856 pts/1    Rs+  05:33   0:00 ps aux

$ docker exec -it without_dumb_init ps aux
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.1  13020 10936 pts/0    Ss+  05:33   0:00 python app.py
root         7  0.0  0.0   8764  6432 pts/0    S+   05:33   0:00 python -c impor
root        14 50.0  0.0   8432  3860 pts/1    Rs+  05:34   0:00 ps aux

docker stop without_dumb_init
docker stop with_dumb_init
```