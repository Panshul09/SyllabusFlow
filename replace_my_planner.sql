-- SyllabusFlow V2: grants and transactional cloud-save function.
-- Run this in Supabase Dashboard -> SQL Editor -> New Query.
-- It assumes the subjects, papers, topics tables and their RLS policies already exist.

grant usage on schema public to authenticated;
grant select, insert, update, delete
on table public.subjects, public.papers, public.topics
to authenticated;

create or replace function public.replace_my_planner(p_subjects jsonb)
returns void
language plpgsql
security invoker
set search_path = ''
as $function$
declare
    v_user_id uuid := (select auth.uid());
    v_subject jsonb;
    v_paper jsonb;
    v_topic jsonb;
    v_subject_id uuid;
    v_paper_id uuid;
begin
    if v_user_id is null then
        raise exception 'Not authenticated';
    end if;

    if jsonb_typeof(coalesce(p_subjects, '[]'::jsonb)) <> 'array' then
        raise exception 'Planner subjects must be a JSON array';
    end if;

    -- Delete and rebuild the caller's planner within one database transaction.
    -- The subject RLS policy ensures this delete can affect only the caller's rows.
    delete from public.subjects
    where user_id = v_user_id;

    for v_subject in
        select item.value
        from jsonb_array_elements(coalesce(p_subjects, '[]'::jsonb)) as item(value)
    loop
        if coalesce(btrim(v_subject ->> 'name'), '') = '' then
            raise exception 'Subject name cannot be empty';
        end if;

        insert into public.subjects (user_id, name)
        values (v_user_id, btrim(v_subject ->> 'name'))
        returning id into v_subject_id;

        for v_paper in
            select item.value
            from jsonb_array_elements(coalesce(v_subject -> 'papers', '[]'::jsonb)) as item(value)
        loop
            if coalesce(btrim(v_paper ->> 'name'), '') = '' then
                raise exception 'Paper name cannot be empty';
            end if;

            insert into public.papers (subject_id, name, code, exam_date)
            values (
                v_subject_id,
                btrim(v_paper ->> 'name'),
                coalesce(v_paper ->> 'code', ''),
                nullif(v_paper ->> 'exam_date', '')::date
            )
            returning id into v_paper_id;

            for v_topic in
                select item.value
                from jsonb_array_elements(coalesce(v_paper -> 'topics', '[]'::jsonb)) as item(value)
            loop
                if coalesce(btrim(v_topic ->> 'name'), '') = '' then
                    raise exception 'Topic name cannot be empty';
                end if;

                insert into public.topics (
                    paper_id, name, difficulty, importance,
                    estimated_hours, completed
                )
                values (
                    v_paper_id,
                    btrim(v_topic ->> 'name'),
                    coalesce(nullif(v_topic ->> 'difficulty', '')::integer, 3),
                    coalesce(nullif(v_topic ->> 'importance', '')::integer, 3),
                    coalesce(nullif(v_topic ->> 'estimated_hours', '')::numeric, 1),
                    coalesce(nullif(v_topic ->> 'completed', '')::boolean, false)
                );
            end loop;
        end loop;
    end loop;
end;
$function$;

-- Keep this function unavailable to unauthenticated callers.
revoke all on function public.replace_my_planner(jsonb) from public;
revoke all on function public.replace_my_planner(jsonb) from anon;
grant execute on function public.replace_my_planner(jsonb) to authenticated;
