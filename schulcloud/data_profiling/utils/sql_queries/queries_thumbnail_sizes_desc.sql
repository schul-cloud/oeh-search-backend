select `thumbnail.large.width` as `width`, `thumbnail.large.height` as `height`, count(*) as `count`
from data
where width <> -1
group by `thumbnail.large.width`, `thumbnail.large.height`
order by `count` desc