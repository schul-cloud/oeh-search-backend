select `lom.general.description`, count(*) as cnt
from data
where `lom.general.description` like "%http%"
group by `lom.general.description`
-- having `lom.general.description` like "%http%"
order by cnt desc
