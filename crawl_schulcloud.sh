#!/bin/bash

working_dir=/root/oeh-search-etl-branches/master_cron/oeh-search-etl
cd $working_dir
source .venv/bin/activate

spiders=(
        "oeh"
        "mediothek_pixiothek"
        "merlin"
)

print_logo=false
show_spider_output=false

# dev, prod | WARNING: It assumes the existence of .env.dev and .env.prod in the converter/ directory. Please refer to
# .env.example for reference environmental variables.
environment="dev"

# Set to true only when $show_spider_output = false. Please prefer to keep to false, at least for crawlings against the
# production machine. (It causes the execution to run in the background and, thus, multiple spiders will run.)
use_nohup=false

# Make the directory "nohups" if it does not already exist.
mkdir -p nohups

###################################
if [ "$print_logo" = true ] ; then
    echo '
                          (
                           )
                          (
                    /\  .-"""-.  /\
                   //\\/  ,,,  \//\\
                   |/\| ,;;;;;, |/\|
                   //\\\;-"""-;///\\
                  //  \/   .   \/  \\
                 (| ,-_| \ | / |_-, |)
                   //`__\.-.-./__`\\
                  // /.-(() ())-.\ \\
                 (\ |)   '---'   (| /)
                  ` (|           |) `
                    \)           (/
   ____  ________  __              _     __
  / __ \/ ____/ / / /  _________  (_)___/ /__  __________
 / / / / __/ / /_/ /  / ___/ __ \/ / __  / _ \/ ___/ ___/
/ /_/ / /___/ __  /  (__  ) /_/ / / /_/ /  __/ /  (__  )
\____/_____/_/ /_/  /____/ .___/_/\__,_/\___/_/  /____/
                        /_/'
fi

if ! test -f "converter/.env.$environment"; then
  echo "converter/.env.$environment does not exist. Exiting..."
  exit 2
else
  cp "converter/.env.$environment" "converter/.env"
fi


# Execute the spiders.
for spider in ${spiders[@]}
do
        echo "Executing $spider spider."

        # Execute the spider
        if [ "$show_spider_output" = true ] ; then
          # ... , save its output to "nohup_SPIDER.out", AND print stdout and stderr.
          scrapy crawl ${spider}_spider -a resetVersion=true | tee -a nohups/nohup_${spider}.out
        elif [ "$show_spider_output" = false ] && [ "$use_nohup" = true ]; then
          # Execute the spider and save its output to two files: "nohup_SPIDER.out" (individual log) and "nohup.out"
          # (collective logs).
          nohup scrapy crawl ${spider}_spider -a resetVersion=true | tee -a nohups/nohup_${spider}.out \
                nohups/nohup.out >/dev/null 2>&1 &
        else # elif [ "$show_spider_output" = false ] && [ "use_nohup" = false ]; then
          # ... and save its output to "nohup_SPIDER.out".
          scrapy crawl ${spider}_spider -a resetVersion=true &> nohups/nohup_${spider}.out
        fi

        echo "Finished with $spider spider"
done
echo "Finished with all spiders! :-)"