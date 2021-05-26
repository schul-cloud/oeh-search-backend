select `lom.technical.location` as `location`, count(*) as `count`
from data
group by `lom.technical.location`
having `count` > 1
order by `count` desc