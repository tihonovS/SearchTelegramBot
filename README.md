# SearchTelegramBot

##start app in background
add environment variable
>export BOT_TOKEN= \

and run in background
>nohup python3 main.py &

##stop app
>ps -x | grep main.py \
>kill -SIGINT pid
