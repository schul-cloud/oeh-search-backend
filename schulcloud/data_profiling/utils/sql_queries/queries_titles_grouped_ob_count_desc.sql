select `lom.general.title`, count(*) as cnt
from data
group by `lom.general.title`
order by cnt desc