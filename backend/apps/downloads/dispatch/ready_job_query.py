"""The SQL that makes bulk downloads fair.

``row_number() OVER (PARTITION BY session_id)`` gives each session's next job
a rank. Ordering by ``rank + already_running`` interleaves sessions, so every
session's Nth job outranks any session's (N+1)th. A user with one video is
dispatched in the same round as the next item of someone's 200-item playlist,
rather than behind all 199 of them.

This is deficit round-robin in about ten lines, riding the partial index
``ix_job_dispatch``.
"""

SELECT_READY_JOBS = """
WITH running AS (
    SELECT session_id, count(*) AS n
      FROM downloads_downloadjob
     WHERE status IN ('dispatched', 'running')
     GROUP BY session_id
),
ready AS (
    SELECT j.id,
           COALESCE(r.n, 0) AS running_n,
           row_number() OVER (
               PARTITION BY j.session_id
               ORDER BY j.priority DESC, j.created_at, j.batch_index NULLS FIRST
           ) AS rn
      FROM downloads_downloadjob j
      LEFT JOIN running r ON r.session_id = j.session_id
     WHERE j.status = 'queued'
       AND j.not_before <= now()
)
SELECT id
  FROM ready
 WHERE rn + running_n <= %(per_session_slots)s
 ORDER BY rn + running_n, random()
 LIMIT %(capacity)s
"""

# Same ranking, used to tell one waiting user their place in line.
SELECT_QUEUE_POSITION = """
WITH running AS (
    SELECT session_id, count(*) AS n
      FROM downloads_downloadjob
     WHERE status IN ('dispatched', 'running')
     GROUP BY session_id
),
ready AS (
    SELECT j.id,
           COALESCE(r.n, 0) AS running_n,
           row_number() OVER (
               PARTITION BY j.session_id
               ORDER BY j.priority DESC, j.created_at, j.batch_index NULLS FIRST
           ) AS rn
      FROM downloads_downloadjob j
      LEFT JOIN running r ON r.session_id = j.session_id
     WHERE j.status = 'queued'
)
SELECT id, rn + running_n AS position FROM ready WHERE id = ANY(%(job_ids)s)
"""
