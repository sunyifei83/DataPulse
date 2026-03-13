"""MCP server wrapper for DataPulse."""

from __future__ import annotations

import argparse
import asyncio
import inspect
import json
import sys
from typing import Any, get_origin

from datapulse.reader import DataPulseReader


async def _run_read_url(url: str, min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    item = await reader.read(url, min_confidence=min_confidence)
    return json.dumps(item.to_dict(), ensure_ascii=False, indent=2)


async def _run_read_batch(urls: list[str], min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    items = await reader.read_batch(urls, min_confidence=min_confidence)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_list_sources(include_inactive: bool = False, public_only: bool = True) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_sources(include_inactive=include_inactive, public_only=public_only), ensure_ascii=False, indent=2)


async def _run_list_packs(public_only: bool = True) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_packs(public_only=public_only), ensure_ascii=False, indent=2)


async def _run_resolve_source(url: str) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.resolve_source(url), ensure_ascii=False, indent=2)


async def _run_list_subscriptions(profile: str = "default") -> str:
    reader = DataPulseReader()
    return json.dumps(reader.list_subscriptions(profile=profile), ensure_ascii=False, indent=2)


async def _run_query_feed(profile: str = "default", source_ids: list[str] | None = None, limit: int = 20,
                        min_confidence: float = 0.0, since: str | None = None) -> str:
    reader = DataPulseReader()
    items = reader.query_feed(profile=profile, source_ids=source_ids, limit=limit, min_confidence=min_confidence, since=since)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_build_json_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.build_json_feed(profile=profile, source_ids=source_ids, limit=limit, min_confidence=min_confidence, since=since)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_build_rss_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    return reader.build_rss_feed(
        profile=profile,
        source_ids=source_ids,
        limit=limit,
        min_confidence=min_confidence,
        since=since,
    )


async def _run_build_digest(
    profile: str = "default",
    source_ids: list[str] | None = None,
    top_n: int = 3,
    secondary_n: int = 7,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.build_digest(
        profile=profile,
        source_ids=source_ids,
        top_n=top_n,
        secondary_n=secondary_n,
        min_confidence=min_confidence,
        since=since,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_emit_digest_package(
    profile: str = "default",
    source_ids: list[str] | None = None,
    top_n: int = 3,
    secondary_n: int = 7,
    min_confidence: float = 0.0,
    since: str | None = None,
    output_format: str = "json",
) -> str:
    reader = DataPulseReader()
    return reader.emit_digest_package(
        profile=profile,
        source_ids=source_ids,
        top_n=top_n,
        secondary_n=secondary_n,
        min_confidence=min_confidence,
        since=since,
        output_format=output_format,
    )


async def _run_story_build(
    profile: str = "default",
    source_ids: list[str] | None = None,
    max_stories: int = 10,
    evidence_limit: int = 6,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.story_build(
        profile=profile,
        source_ids=source_ids,
        max_stories=max_stories,
        evidence_limit=evidence_limit,
        min_confidence=min_confidence,
        since=since,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_story_list(limit: int = 20, min_items: int = 1) -> str:
    reader = DataPulseReader()
    payload = reader.list_stories(limit=limit, min_items=min_items)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_story_show(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_story(identifier)
    return json.dumps({"ok": payload is not None, "story": payload}, ensure_ascii=False, indent=2)


async def _run_story_update(
    identifier: str,
    *,
    title: str | None = None,
    summary: str | None = None,
    status: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.update_story(identifier, title=title, summary=summary, status=status)
    return json.dumps({"ok": payload is not None, "story": payload}, ensure_ascii=False, indent=2)


async def _run_story_graph(identifier: str, entity_limit: int = 12, relation_limit: int = 24) -> str:
    reader = DataPulseReader()
    payload = reader.story_graph(identifier, entity_limit=entity_limit, relation_limit=relation_limit)
    return json.dumps({"ok": payload is not None, "graph": payload}, ensure_ascii=False, indent=2)


async def _run_story_export(identifier: str, output_format: str = "json") -> str:
    reader = DataPulseReader()
    payload = reader.export_story(identifier, output_format=output_format)
    if payload is None:
        return json.dumps({"ok": False, "story": None}, ensure_ascii=False, indent=2)
    return payload


async def _run_build_atom_feed(
    profile: str = "default",
    source_ids: list[str] | None = None,
    limit: int = 20,
    min_confidence: float = 0.0,
    since: str | None = None,
) -> str:
    reader = DataPulseReader()
    return reader.build_atom_feed(
        profile=profile,
        source_ids=source_ids,
        limit=limit,
        min_confidence=min_confidence,
        since=since,
    )


async def _run_subscribe_source(profile: str, source_id: str) -> str:
    reader = DataPulseReader()
    ok = reader.subscribe_source(source_id, profile=profile)
    return json.dumps({"ok": ok, "source_id": source_id, "profile": profile}, ensure_ascii=False, indent=2)


async def _run_unsubscribe_source(profile: str, source_id: str) -> str:
    reader = DataPulseReader()
    ok = reader.unsubscribe_source(source_id, profile=profile)
    return json.dumps({"ok": ok, "source_id": source_id, "profile": profile}, ensure_ascii=False, indent=2)


async def _run_mark_processed(item_id: str, processed: bool = True) -> str:
    reader = DataPulseReader()
    ok = reader.mark_processed(item_id, processed=processed)
    return json.dumps({"ok": ok}, ensure_ascii=False, indent=2)


async def _run_query_unprocessed(limit: int = 20, min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    items = reader.query_unprocessed(limit=limit, min_confidence=min_confidence)
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_list_report_briefs(limit: int = 20, status: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.list_report_briefs(limit=limit, status=status)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_report_brief(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_report_brief(**payload), ensure_ascii=False, indent=2)


async def _run_show_report_brief(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_report_brief(identifier)
    return json.dumps({"ok": payload is not None, "report_brief": payload}, ensure_ascii=False, indent=2)


async def _run_update_report_brief(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_report_brief(identifier, **payload)
    return json.dumps({"ok": updated is not None, "report_brief": updated}, ensure_ascii=False, indent=2)


async def _run_list_claim_cards(limit: int = 20, status: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.list_claim_cards(limit=limit, status=status)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_claim_card(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_claim_card(**payload), ensure_ascii=False, indent=2)


async def _run_show_claim_card(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_claim_card(identifier)
    return json.dumps({"ok": payload is not None, "claim_card": payload}, ensure_ascii=False, indent=2)


async def _run_update_claim_card(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_claim_card(identifier, **payload)
    return json.dumps({"ok": updated is not None, "claim_card": updated}, ensure_ascii=False, indent=2)


async def _run_list_report_sections(limit: int = 20, status: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.list_report_sections(limit=limit, status=status)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_report_section(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_report_section(**payload), ensure_ascii=False, indent=2)


async def _run_show_report_section(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_report_section(identifier)
    return json.dumps({"ok": payload is not None, "report_section": payload}, ensure_ascii=False, indent=2)


async def _run_update_report_section(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_report_section(identifier, **payload)
    return json.dumps({"ok": updated is not None, "report_section": updated}, ensure_ascii=False, indent=2)


async def _run_list_citation_bundles(limit: int = 20) -> str:
    reader = DataPulseReader()
    payload = reader.list_citation_bundles(limit=limit)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_citation_bundle(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_citation_bundle(**payload), ensure_ascii=False, indent=2)


async def _run_show_citation_bundle(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_citation_bundle(identifier)
    return json.dumps({"ok": payload is not None, "citation_bundle": payload}, ensure_ascii=False, indent=2)


async def _run_update_citation_bundle(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_citation_bundle(identifier, **payload)
    return json.dumps({"ok": updated is not None, "citation_bundle": updated}, ensure_ascii=False, indent=2)


async def _run_list_reports(limit: int = 20, status: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.list_reports(limit=limit, status=status)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_report(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_report(**payload), ensure_ascii=False, indent=2)


async def _run_show_report(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_report(identifier)
    return json.dumps({"ok": payload is not None, "report": payload}, ensure_ascii=False, indent=2)


async def _run_update_report(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_report(identifier, **payload)
    return json.dumps({"ok": updated is not None, "report": updated}, ensure_ascii=False, indent=2)


async def _run_compose_report(
    identifier: str,
    profile_id: str | None = None,
    include_sections: bool | None = None,
    include_claim_cards: bool | None = None,
    include_citation_bundles: bool | None = None,
    include_export_profiles: bool | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.compose_report(
        identifier,
        profile_id=profile_id,
        include_sections=include_sections,
        include_claim_cards=include_claim_cards,
        include_citation_bundles=include_citation_bundles,
        include_export_profiles=include_export_profiles,
    )
    return json.dumps({"ok": payload is not None, "report": payload}, ensure_ascii=False, indent=2)


async def _run_report_quality(
    identifier: str,
    profile_id: str | None = None,
    include_sections: bool | None = None,
    include_claim_cards: bool | None = None,
    include_citation_bundles: bool | None = None,
    include_export_profiles: bool | None = None,
) -> str:
    reader = DataPulseReader()
    quality = reader.assess_report_quality(
        identifier,
        profile_id=profile_id,
        include_sections=include_sections,
        include_claim_cards=include_claim_cards,
        include_citation_bundles=include_citation_bundles,
        include_export_profiles=include_export_profiles,
    )
    return json.dumps({"ok": quality is not None, "quality": quality}, ensure_ascii=False, indent=2)


async def _run_export_report(
    identifier: str,
    profile_id: str | None = None,
    output_format: str = "json",
    include_sections: bool | None = None,
    include_claim_cards: bool | None = None,
    include_citation_bundles: bool | None = None,
    include_metadata: bool | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.export_report(
        identifier,
        profile_id=profile_id,
        output_format=output_format,
        include_sections=include_sections,
        include_claim_cards=include_claim_cards,
        include_citation_bundles=include_citation_bundles,
        include_metadata=include_metadata,
    )
    if payload is None:
        return json.dumps({"ok": False, "report": None}, ensure_ascii=False, indent=2)
    if payload and output_format in {"json", "markdown", "md"}:
        return payload
    return json.dumps({"ok": False, "report": None, "error": "unsupported output format"}, ensure_ascii=False, indent=2)


async def _run_list_export_profiles(limit: int = 20, status: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.list_export_profiles(limit=limit, status=status)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_export_profile(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    return json.dumps(reader.create_export_profile(**payload), ensure_ascii=False, indent=2)


async def _run_show_export_profile(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_export_profile(identifier)
    return json.dumps({"ok": payload is not None, "export_profile": payload}, ensure_ascii=False, indent=2)


async def _run_update_export_profile(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_export_profile(identifier, **payload)
    return json.dumps({"ok": updated is not None, "export_profile": updated}, ensure_ascii=False, indent=2)


async def _run_list_delivery_subscriptions(
    limit: int = 20,
    status: str | None = None,
    subject_kind: str | None = None,
    subject_ref: str | None = None,
    output_kind: str | None = None,
    delivery_mode: str | None = None,
    route_name: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.list_delivery_subscriptions(
        limit=limit,
        status=status,
        subject_kind=subject_kind,
        subject_ref=subject_ref,
        output_kind=output_kind,
        delivery_mode=delivery_mode,
        route_name=route_name,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_create_delivery_subscription(payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    created = reader.create_delivery_subscription(**payload)
    return json.dumps(created, ensure_ascii=False, indent=2)


async def _run_show_delivery_subscription(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_delivery_subscription(identifier)
    return json.dumps({"ok": payload is not None, "delivery_subscription": payload}, ensure_ascii=False, indent=2)


async def _run_update_delivery_subscription(identifier: str, payload: dict[str, Any] | None = None) -> str:
    reader = DataPulseReader()
    payload = payload or {}
    if not isinstance(payload, dict):
        raise TypeError("payload must be an object")
    updated = reader.update_delivery_subscription(identifier, **payload)
    return json.dumps({"ok": updated is not None, "delivery_subscription": updated}, ensure_ascii=False, indent=2)


async def _run_delete_delivery_subscription(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.delete_delivery_subscription(identifier)
    return json.dumps({"ok": payload is not None, "delivery_subscription": payload}, ensure_ascii=False, indent=2)


async def _run_list_delivery_dispatch_records(
    limit: int = 20,
    status: str | None = None,
    subscription_id: str | None = None,
    subject_kind: str | None = None,
    subject_ref: str | None = None,
    output_kind: str | None = None,
    route_name: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.list_delivery_dispatch_records(
        limit=limit,
        status=status,
        subscription_id=subscription_id,
        subject_kind=subject_kind,
        subject_ref=subject_ref,
        output_kind=output_kind,
        route_name=route_name,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_build_report_delivery_package(subscription_identifier: str, profile_id: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.build_report_delivery_package(subscription_identifier, profile_id=profile_id)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_dispatch_report_delivery(subscription_identifier: str, profile_id: str | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.dispatch_report_delivery(subscription_identifier, profile_id=profile_id)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_triage_list(
    limit: int = 20,
    min_confidence: float = 0.0,
    states: list[str] | None = None,
    include_closed: bool = False,
) -> str:
    reader = DataPulseReader()
    payload = reader.triage_list(
        limit=limit,
        min_confidence=min_confidence,
        states=states,
        include_closed=include_closed,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_triage_update(
    item_id: str,
    state: str,
    note: str = "",
    actor: str = "mcp",
    duplicate_of: str | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.triage_update(
        item_id,
        state=state,
        note=note,
        actor=actor,
        duplicate_of=duplicate_of,
    )
    return json.dumps({"ok": payload is not None, "item": payload}, ensure_ascii=False, indent=2)


async def _run_triage_note(item_id: str, note: str, author: str = "mcp") -> str:
    reader = DataPulseReader()
    payload = reader.triage_note(item_id, note=note, author=author)
    return json.dumps({"ok": payload is not None, "item": payload}, ensure_ascii=False, indent=2)


async def _run_triage_stats(min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    payload = reader.triage_stats(min_confidence=min_confidence)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_triage_explain(item_id: str, limit: int = 5) -> str:
    reader = DataPulseReader()
    payload = reader.triage_explain(item_id, limit=limit)
    return json.dumps({"ok": payload is not None, "explanation": payload}, ensure_ascii=False, indent=2)


async def _run_search_web(
    query: str,
    sites: list[str] | None = None,
    platform: str | None = None,
    limit: int = 5,
    fetch_content: bool = True,
    extract_entities: bool = False,
    entity_mode: str = "fast",
    store_entities: bool = True,
    entity_api_key: str | None = None,
    entity_model: str = "gpt-4o-mini",
    entity_api_base: str = "https://api.openai.com/v1",
    min_confidence: float = 0.0,
    provider: str = "auto",
    mode: str = "single",
    deep: bool = False,
    news: bool = False,
    time_range: str | None = None,
    freshness: str | None = None,
) -> str:
    reader = DataPulseReader()
    requested_time_range = time_range or freshness
    items = await reader.search(
        query,
        sites=sites,
        platform=platform,
        limit=limit,
        fetch_content=fetch_content,
        extract_entities=extract_entities,
        entity_mode=entity_mode,
        store_entities=store_entities,
        entity_api_key=entity_api_key,
        entity_model=entity_model,
        entity_api_base=entity_api_base,
        min_confidence=min_confidence,
        provider=provider,
        mode=mode,
        deep=deep,
        news=news,
        time_range=requested_time_range,
    )
    return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)


async def _run_trending(
    location: str = "",
    top_n: int = 20,
    store: bool = False,
    validate: bool = False,
    validate_mode: str = "strict",
) -> str:
    reader = DataPulseReader()
    result = await reader.trending(
        location=location,
        top_n=top_n,
        store=store,
        validate=validate,
        validate_mode=validate_mode,
    )
    return json.dumps(result, ensure_ascii=False, indent=2)


async def _run_extract_entities(
    url: str,
    mode: str = "fast",
    store_entities: bool = True,
    llm_api_key: str | None = None,
    llm_model: str = "gpt-4o-mini",
    llm_api_base: str = "https://api.openai.com/v1",
) -> str:
    reader = DataPulseReader()
    payload = await reader.extract_entities(
        url,
        mode=mode,
        store=store_entities,
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        llm_api_base=llm_api_base,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_query_entities(
    entity_type: str = "",
    name: str = "",
    min_sources: int = 1,
    limit: int = 50,
) -> str:
    reader = DataPulseReader()
    payload = reader.query_entities(
        entity_type=entity_type or None,
        name=name,
        min_sources=min_sources,
        limit=limit,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_entity_graph(entity_name: str, limit: int = 50) -> str:
    reader = DataPulseReader()
    return json.dumps(reader.entity_graph(entity_name=entity_name, limit=limit), ensure_ascii=False, indent=2)


async def _run_entity_stats() -> str:
    reader = DataPulseReader()
    return json.dumps(reader.entity_stats(), ensure_ascii=False, indent=2)


async def _run_doctor() -> str:
    reader = DataPulseReader()
    report = reader.doctor()
    return json.dumps(report, ensure_ascii=False, indent=2)


async def _run_read_url_advanced(
    url: str,
    target_selector: str = "",
    wait_for_selector: str = "",
    no_cache: bool = False,
    with_alt: bool = False,
    min_confidence: float = 0.0,
) -> str:
    from datapulse.collectors.jina import JinaCollector

    reader = DataPulseReader()
    # Replace the default Jina collector with an enhanced one
    enhanced = JinaCollector(
        target_selector=target_selector,
        wait_for_selector=wait_for_selector,
        no_cache=no_cache,
        with_alt=with_alt,
    )
    for i, p in enumerate(reader.router.parsers):
        if getattr(p, "name", "") == "jina":
            reader.router.parsers[i] = enhanced
            break
    item = await reader.read(url, min_confidence=min_confidence)
    return json.dumps(item.to_dict(), ensure_ascii=False, indent=2)


async def _run_install_pack(profile: str, slug: str) -> str:
    reader = DataPulseReader()
    added = reader.install_pack(slug=slug, profile=profile)
    return json.dumps({"ok": added > 0, "added": added, "slug": slug, "profile": profile}, ensure_ascii=False, indent=2)


async def _run_create_watch(
    name: str,
    query: str,
    platforms: list[str] | None = None,
    sites: list[str] | None = None,
    schedule: str = "manual",
    min_confidence: float = 0.0,
    top_n: int = 5,
    alert_rules: list[dict[str, Any]] | None = None,
) -> str:
    reader = DataPulseReader()
    payload = reader.create_watch(
        name=name,
        query=query,
        platforms=platforms,
        sites=sites,
        schedule=schedule,
        min_confidence=min_confidence,
        top_n=top_n,
        alert_rules=alert_rules,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_list_watches(include_disabled: bool = False) -> str:
    reader = DataPulseReader()
    payload = reader.list_watches(include_disabled=include_disabled)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_watch_show(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.show_watch(identifier)
    return json.dumps({"ok": payload is not None, "mission": payload}, ensure_ascii=False, indent=2)


async def _run_watch_set_alert_rules(identifier: str, alert_rules: list[dict[str, Any]] | None = None) -> str:
    reader = DataPulseReader()
    payload = reader.set_watch_alert_rules(identifier, alert_rules=alert_rules)
    return json.dumps({"ok": payload is not None, "mission": payload}, ensure_ascii=False, indent=2)


async def _run_watch_results(identifier: str, limit: int = 10, min_confidence: float = 0.0) -> str:
    reader = DataPulseReader()
    payload = reader.list_watch_results(identifier, limit=limit, min_confidence=min_confidence)
    return json.dumps({"ok": payload is not None, "results": payload or []}, ensure_ascii=False, indent=2)


async def _run_run_watch(identifier: str) -> str:
    reader = DataPulseReader()
    payload = await reader.run_watch(identifier)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_disable_watch(identifier: str) -> str:
    reader = DataPulseReader()
    payload = reader.disable_watch(identifier)
    return json.dumps(
        {"ok": payload is not None, "mission": payload, "identifier": identifier},
        ensure_ascii=False,
        indent=2,
    )


async def _run_run_due_watches(limit: int = 0) -> str:
    reader = DataPulseReader()
    payload = await reader.run_due_watches(limit=limit or None)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_list_alerts(limit: int = 20, mission_id: str = "") -> str:
    reader = DataPulseReader()
    payload = reader.list_alerts(limit=limit, mission_id=mission_id or None)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_list_alert_routes() -> str:
    reader = DataPulseReader()
    payload = reader.list_alert_routes()
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_alert_route_health(limit: int = 100) -> str:
    reader = DataPulseReader()
    payload = reader.alert_route_health(limit=limit)
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_watch_status() -> str:
    reader = DataPulseReader()
    payload = reader.watch_status_snapshot()
    return json.dumps(payload, ensure_ascii=False, indent=2)


async def _run_ops_overview(alert_limit: int = 8, route_limit: int = 100, recent_failure_limit: int = 5) -> str:
    reader = DataPulseReader()
    payload = reader.ops_snapshot(
        alert_limit=alert_limit,
        route_limit=route_limit,
        recent_failure_limit=recent_failure_limit,
    )
    return json.dumps(payload, ensure_ascii=False, indent=2)


class _LocalMCP:
    """Minimal stdlib MCP-compatible runtime fallback."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    @staticmethod
    def _json_type(annotation: Any) -> str:
        if isinstance(annotation, str):
            ann = annotation.strip().lower()
            if ann.startswith(("list[", "tuple[", "set[")):
                return "array"
            return {"str": "string", "string": "string",
                    "int": "integer", "integer": "integer",
                    "float": "number", "bool": "boolean", "boolean": "boolean",
                    "dict": "object", "list": "array", "tuple": "array", "set": "array"}.get(ann, "string")
        origin = get_origin(annotation)
        if annotation in {str, int, float, bool, None}:
            return {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean",
                None: "null",
            }[annotation]
        if origin in {list, tuple, set}:
            return "array"
        if origin is dict:
            return "object"
        if origin is not None:
            return "string"
        return "string"

    def _tool_schema(self, func: Any) -> dict[str, Any]:
        signature = inspect.signature(func)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for name, parameter in signature.parameters.items():
            if parameter.kind in {parameter.VAR_KEYWORD, parameter.VAR_POSITIONAL}:
                continue
            annotation = parameter.annotation if parameter.annotation is not parameter.empty else str
            field: dict[str, Any] = {"type": self._json_type(annotation)}
            if parameter.default is parameter.empty:
                required.append(name)
            else:
                field["default"] = parameter.default
            properties[name] = field

        return {
            "name": func.__name__,
            "description": (inspect.getdoc(func) or "").strip() or func.__name__,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def _tool_metadata(self) -> list[dict[str, Any]]:
        return [self._tool_schema(func) for _, func in self.tools.items()]

    def _build_response(
        self,
        request_id: Any,
        result: Any = None,
        error: str | None = None,
        error_code: int = -32603,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
        if error is None:
            payload["result"] = result
        else:
            payload["error"] = {"code": error_code, "message": error}
        return payload

    async def _run_tool(self, name: str | None, arguments: Any) -> str:
        if not name:
            raise ValueError("tool name is required")
        if name not in self.tools:
            raise KeyError(f"tool not found: {name}")
        if not isinstance(arguments, dict):
            raise TypeError("tool arguments must be a JSON object")

        handler = self.tools[name]
        result = handler(**arguments)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    def _emit(self, message: dict[str, Any] | list[dict[str, Any]]) -> None:
        print(json.dumps(message, ensure_ascii=False), flush=True)

    def _handle_stdio_request(self, message: Any) -> list[dict[str, Any]]:
        if not isinstance(message, dict):
            return [self._build_response(None, error="Invalid Request", error_code=-32600)]

        request_id = message.get("id")
        method = message.get("method")
        if not method:
            if request_id is None:
                return []
            return [self._build_response(request_id, error="Invalid Request", error_code=-32600)]

        if method in {"notifications/initialized", "initialized", "ping", "notifications/shutdown"}:
            return []

        if method == "initialize":
            if request_id is None:
                return []
            return [
                self._build_response(
                    request_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": self.name, "version": "1.0"},
                    },
                )
            ]

        if method == "tools/list":
            if request_id is None:
                return []
            return [self._build_response(request_id, {"tools": self._tool_metadata()})]

        if method == "tools/call":
            params = message.get("params")
            if request_id is None:
                return []
            if not isinstance(params, dict):
                return [self._build_response(request_id, error="Invalid params: must be object", error_code=-32602)]
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(tool_name, str) or not tool_name:
                return [self._build_response(request_id, error="Invalid params: tool name is required", error_code=-32602)]
            if not isinstance(arguments, dict):
                return [self._build_response(request_id, error="Invalid params: arguments must be object", error_code=-32602)]
            try:
                result = asyncio.run(self._run_tool(tool_name, arguments))
            except KeyError as exc:
                return [self._build_response(request_id, error=str(exc), error_code=-32601)]
            except Exception as exc:
                return [self._build_response(request_id, error=str(exc), error_code=-32603)]
            return [
                self._build_response(
                    request_id,
                    {
                        "content": [{"type": "text", "text": result}],
                        "isError": False,
                    },
                )
            ]

        if method == "shutdown":
            if request_id is None:
                return []
            return [self._build_response(request_id, {"ok": True})]

        if method in {"notifications/cancelled", "notifications/progress"}:
            return []

        if request_id is not None:
            return [self._build_response(request_id, error=f"Unsupported method: {method}", error_code=-32601)]
        return []

    def _run_stdio_loop(self) -> None:
        while True:
            raw_line = sys.stdin.readline()
            if not raw_line:
                break
            line = raw_line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                self._emit(self._build_response(None, error="Parse error", error_code=-32700))
                continue

            responses: list[dict[str, Any]] = []
            if isinstance(message, list):
                if not message:
                    responses.append(self._build_response(None, error="Invalid Request", error_code=-32600))
                else:
                    for item in message:
                        responses.extend(self._handle_stdio_request(item))
            else:
                responses.extend(self._handle_stdio_request(message))

            if not responses:
                continue
            if len(responses) == 1:
                self._emit(responses[0])
            else:
                self._emit(responses)

    def run(self) -> None:
        parser = argparse.ArgumentParser(
            prog="python -m datapulse.mcp_server",
            description="DataPulse MCP-compatible server (fast local fallback when dependency is unavailable).",
        )
        parser.add_argument("--list-tools", action="store_true", help="List all registered tools as JSON.")
        parser.add_argument("--call", help="Call one tool directly by name.")
        parser.add_argument("--args", default="{}", help="Tool arguments as JSON string.")
        parser.add_argument(
            "--stdio",
            action="store_true",
            help="Start stdio JSON-RPC loop (default when no explicit action).",
        )
        parsed = parser.parse_args()

        if parsed.list_tools:
            print(json.dumps(self._tool_metadata(), ensure_ascii=False, indent=2))
            return

        if parsed.call:
            try:
                arguments = json.loads(parsed.args or "{}")
            except json.JSONDecodeError as exc:
                raise SystemExit(f"--args must be valid JSON: {exc}")
            if not isinstance(arguments, dict):
                raise SystemExit("--args must be a JSON object")
            result = asyncio.run(self._run_tool(parsed.call, arguments))
            print(result)
            return

        if parsed.stdio or not sys.argv[1:]:
            self._run_stdio_loop()
            return

        parser.print_help()


def _register_tools(app: Any) -> None:
    @app.tool()
    async def read_url(url: str, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_read_url(url, min_confidence=min_confidence)

    @app.tool()
    async def read_batch(urls: list[str], min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_read_batch(urls, min_confidence=min_confidence)

    @app.tool()
    async def list_sources(include_inactive: bool = False, public_only: bool = True) -> str:  # noqa: ANN001
        return await _run_list_sources(include_inactive=include_inactive, public_only=public_only)

    @app.tool()
    async def list_packs(public_only: bool = True) -> str:  # noqa: ANN001
        return await _run_list_packs(public_only=public_only)

    @app.tool()
    async def resolve_source(url: str) -> str:  # noqa: ANN001
        return await _run_resolve_source(url)

    @app.tool()
    async def list_subscriptions(profile: str = "default") -> str:  # noqa: ANN001
        return await _run_list_subscriptions(profile=profile)

    @app.tool()
    async def source_subscribe(profile: str, source_id: str) -> str:  # noqa: ANN001
        return await _run_subscribe_source(profile=profile, source_id=source_id)

    @app.tool()
    async def source_unsubscribe(profile: str, source_id: str) -> str:  # noqa: ANN001
        return await _run_unsubscribe_source(profile=profile, source_id=source_id)

    @app.tool()
    async def install_pack(profile: str, slug: str) -> str:  # noqa: ANN001
        return await _run_install_pack(profile=profile, slug=slug)

    @app.tool()
    async def create_watch(
        name: str,
        query: str,
        platforms: list[str] | None = None,
        sites: list[str] | None = None,
        schedule: str = "manual",
        min_confidence: float = 0.0,
        top_n: int = 5,
        alert_rules: list[dict[str, Any]] | None = None,
    ) -> str:
        """Create a recurring watch mission for a saved query."""
        return await _run_create_watch(
            name=name,
            query=query,
            platforms=platforms,
            sites=sites,
            schedule=schedule,
            min_confidence=min_confidence,
            top_n=top_n,
            alert_rules=alert_rules,
        )

    @app.tool()
    async def list_watches(include_disabled: bool = False) -> str:
        """List configured watch missions."""
        return await _run_list_watches(include_disabled=include_disabled)

    @app.tool()
    async def watch_show(identifier: str) -> str:
        """Show one watch mission with recent runs, persisted results, recent alerts, and retry advice."""
        return await _run_watch_show(identifier=identifier)

    @app.tool()
    async def watch_set_alert_rules(identifier: str, alert_rules: list[dict[str, Any]] | None = None) -> str:
        """Replace alert rules for one watch mission. Pass an empty list to clear rules."""
        return await _run_watch_set_alert_rules(identifier=identifier, alert_rules=alert_rules)

    @app.tool()
    async def watch_results(identifier: str, limit: int = 10, min_confidence: float = 0.0) -> str:
        """Show recent persisted results for one watch mission."""
        return await _run_watch_results(identifier=identifier, limit=limit, min_confidence=min_confidence)

    @app.tool()
    async def run_watch(identifier: str) -> str:
        """Run one watch mission by id or name."""
        return await _run_run_watch(identifier=identifier)

    @app.tool()
    async def disable_watch(identifier: str) -> str:
        """Disable one watch mission by id or name."""
        return await _run_disable_watch(identifier=identifier)

    @app.tool()
    async def run_due_watches(limit: int = 0) -> str:
        """Run all currently due watch missions once."""
        return await _run_run_due_watches(limit=limit)

    @app.tool()
    async def list_alerts(limit: int = 20, mission_id: str = "") -> str:
        """List stored watch alert events."""
        return await _run_list_alerts(limit=limit, mission_id=mission_id)

    @app.tool()
    async def list_alert_routes() -> str:
        """List configured named alert delivery routes."""
        return await _run_list_alert_routes()

    @app.tool()
    async def alert_route_health(limit: int = 100) -> str:
        """Show delivery health for named alert routes."""
        return await _run_alert_route_health(limit=limit)

    @app.tool()
    async def watch_status() -> str:
        """Show watch daemon heartbeat and metrics."""
        return await _run_watch_status()

    @app.tool()
    async def ops_overview(alert_limit: int = 8, route_limit: int = 100, recent_failure_limit: int = 5) -> str:
        """Show a unified ops snapshot across collector health, watch metrics, route delivery, and recent failures."""
        return await _run_ops_overview(
            alert_limit=alert_limit,
            route_limit=route_limit,
            recent_failure_limit=recent_failure_limit,
        )

    @app.tool()
    async def query_feed(profile: str = "default", source_ids: list[str] | None = None,
                        limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_query_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_json_feed(profile: str = "default", source_ids: list[str] | None = None,
                             limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_json_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_rss_feed(profile: str = "default", source_ids: list[str] | None = None,
                            limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_rss_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_atom_feed(profile: str = "default", source_ids: list[str] | None = None,
                              limit: int = 20, min_confidence: float = 0.0, since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_atom_feed(
            profile=profile,
            source_ids=source_ids,
            limit=limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def build_digest(profile: str = "default", source_ids: list[str] | None = None,
                           top_n: int = 3, secondary_n: int = 7, min_confidence: float = 0.0,
                           since: str | None = None) -> str:  # noqa: ANN001
        return await _run_build_digest(
            profile=profile,
            source_ids=source_ids,
            top_n=top_n,
            secondary_n=secondary_n,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def emit_digest_package(
        profile: str = "default",
        source_ids: list[str] | None = None,
        top_n: int = 3,
        secondary_n: int = 7,
        min_confidence: float = 0.0,
        since: str | None = None,
        output_format: str = "json",
    ) -> str:  # noqa: ANN001
        """Export digest package for office automation integrations (read-only payload)."""
        return await _run_emit_digest_package(
            profile=profile,
            source_ids=source_ids,
            top_n=top_n,
            secondary_n=secondary_n,
            min_confidence=min_confidence,
            since=since,
            output_format=output_format,
        )

    @app.tool()
    async def story_build(
        profile: str = "default",
        source_ids: list[str] | None = None,
        max_stories: int = 10,
        evidence_limit: int = 6,
        min_confidence: float = 0.0,
        since: str | None = None,
    ) -> str:  # noqa: ANN001
        """Build and persist a clustered story workspace snapshot."""
        return await _run_story_build(
            profile=profile,
            source_ids=source_ids,
            max_stories=max_stories,
            evidence_limit=evidence_limit,
            min_confidence=min_confidence,
            since=since,
        )

    @app.tool()
    async def story_list(limit: int = 20, min_items: int = 1) -> str:  # noqa: ANN001
        """List persisted stories from the story workspace."""
        return await _run_story_list(limit=limit, min_items=min_items)

    @app.tool()
    async def story_show(identifier: str) -> str:  # noqa: ANN001
        """Show one persisted story by id or title."""
        return await _run_story_show(identifier=identifier)

    @app.tool()
    async def story_update(
        identifier: str,
        title: str | None = None,
        summary: str | None = None,
        status: str | None = None,
    ) -> str:  # noqa: ANN001
        """Update one persisted story by id or title."""
        return await _run_story_update(
            identifier=identifier,
            title=title,
            summary=summary,
            status=status,
        )

    @app.tool()
    async def story_graph(identifier: str, entity_limit: int = 12, relation_limit: int = 24) -> str:  # noqa: ANN001
        """Show the entity graph for one persisted story."""
        return await _run_story_graph(
            identifier=identifier,
            entity_limit=entity_limit,
            relation_limit=relation_limit,
        )

    @app.tool()
    async def story_export(identifier: str, output_format: str = "json") -> str:  # noqa: ANN001
        """Export one story as JSON or Markdown."""
        return await _run_story_export(identifier=identifier, output_format=output_format)

    @app.tool()
    async def list_report_briefs(limit: int = 20, status: str | None = None) -> str:
        """List persisted report briefs."""
        return await _run_list_report_briefs(limit=limit, status=status)

    @app.tool()
    async def create_report_brief(payload: dict[str, Any] | None = None) -> str:
        """Create one report brief."""
        return await _run_create_report_brief(payload=payload)

    @app.tool()
    async def show_report_brief(identifier: str) -> str:
        """Show one report brief."""
        return await _run_show_report_brief(identifier=identifier)

    @app.tool()
    async def update_report_brief(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one report brief."""
        return await _run_update_report_brief(identifier=identifier, payload=payload)

    @app.tool()
    async def list_claim_cards(limit: int = 20, status: str | None = None) -> str:
        """List persisted claim cards."""
        return await _run_list_claim_cards(limit=limit, status=status)

    @app.tool()
    async def create_claim_card(payload: dict[str, Any] | None = None) -> str:
        """Create one claim card."""
        return await _run_create_claim_card(payload=payload)

    @app.tool()
    async def show_claim_card(identifier: str) -> str:
        """Show one claim card."""
        return await _run_show_claim_card(identifier=identifier)

    @app.tool()
    async def update_claim_card(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one claim card."""
        return await _run_update_claim_card(identifier=identifier, payload=payload)

    @app.tool()
    async def list_report_sections(limit: int = 20, status: str | None = None) -> str:
        """List persisted report sections."""
        return await _run_list_report_sections(limit=limit, status=status)

    @app.tool()
    async def create_report_section(payload: dict[str, Any] | None = None) -> str:
        """Create one report section."""
        return await _run_create_report_section(payload=payload)

    @app.tool()
    async def show_report_section(identifier: str) -> str:
        """Show one report section."""
        return await _run_show_report_section(identifier=identifier)

    @app.tool()
    async def update_report_section(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one report section."""
        return await _run_update_report_section(identifier=identifier, payload=payload)

    @app.tool()
    async def list_citation_bundles(limit: int = 20) -> str:
        """List persisted citation bundles."""
        return await _run_list_citation_bundles(limit=limit)

    @app.tool()
    async def create_citation_bundle(payload: dict[str, Any] | None = None) -> str:
        """Create one citation bundle."""
        return await _run_create_citation_bundle(payload=payload)

    @app.tool()
    async def show_citation_bundle(identifier: str) -> str:
        """Show one citation bundle."""
        return await _run_show_citation_bundle(identifier=identifier)

    @app.tool()
    async def update_citation_bundle(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one citation bundle."""
        return await _run_update_citation_bundle(identifier=identifier, payload=payload)

    @app.tool()
    async def list_reports(limit: int = 20, status: str | None = None) -> str:
        """List persisted reports."""
        return await _run_list_reports(limit=limit, status=status)

    @app.tool()
    async def create_report(payload: dict[str, Any] | None = None) -> str:
        """Create one report object."""
        return await _run_create_report(payload=payload)

    @app.tool()
    async def show_report(identifier: str) -> str:
        """Show one report by identifier."""
        return await _run_show_report(identifier=identifier)

    @app.tool()
    async def update_report(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one report."""
        return await _run_update_report(identifier=identifier, payload=payload)

    @app.tool()
    async def compose_report(
        identifier: str,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_export_profiles: bool | None = None,
    ) -> str:
        """Assemble a report including optional guards and components."""
        return await _run_compose_report(
            identifier=identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )

    @app.tool()
    async def assess_report_quality(
        identifier: str,
        profile_id: str | None = None,
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_export_profiles: bool | None = None,
    ) -> str:
        """Assess report quality for one assembled report."""
        return await _run_report_quality(
            identifier=identifier,
            profile_id=profile_id,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_export_profiles=include_export_profiles,
        )

    @app.tool()
    async def export_report(
        identifier: str,
        profile_id: str | None = None,
        output_format: str = "json",
        include_sections: bool | None = None,
        include_claim_cards: bool | None = None,
        include_citation_bundles: bool | None = None,
        include_metadata: bool | None = None,
    ) -> str:  # noqa: ANN001
        """Export one report."""
        return await _run_export_report(
            identifier=identifier,
            profile_id=profile_id,
            output_format=output_format,
            include_sections=include_sections,
            include_claim_cards=include_claim_cards,
            include_citation_bundles=include_citation_bundles,
            include_metadata=include_metadata,
        )

    @app.tool()
    async def list_export_profiles(limit: int = 20, status: str | None = None) -> str:
        """List persisted export profiles."""
        return await _run_list_export_profiles(limit=limit, status=status)

    @app.tool()
    async def create_export_profile(payload: dict[str, Any] | None = None) -> str:
        """Create one export profile."""
        return await _run_create_export_profile(payload=payload)

    @app.tool()
    async def show_export_profile(identifier: str) -> str:
        """Show one export profile."""
        return await _run_show_export_profile(identifier=identifier)

    @app.tool()
    async def update_export_profile(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one export profile."""
        return await _run_update_export_profile(identifier=identifier, payload=payload)

    @app.tool()
    async def list_delivery_subscriptions(
        limit: int = 20,
        status: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        delivery_mode: str | None = None,
        route_name: str | None = None,
    ) -> str:
        """List normalized delivery subscriptions across report, story, watch, and profile subjects."""
        return await _run_list_delivery_subscriptions(
            limit=limit,
            status=status,
            subject_kind=subject_kind,
            subject_ref=subject_ref,
            output_kind=output_kind,
            delivery_mode=delivery_mode,
            route_name=route_name,
        )

    @app.tool()
    async def create_delivery_subscription(payload: dict[str, Any] | None = None) -> str:
        """Create one normalized delivery subscription."""
        return await _run_create_delivery_subscription(payload=payload)

    @app.tool()
    async def show_delivery_subscription(identifier: str) -> str:
        """Show one normalized delivery subscription."""
        return await _run_show_delivery_subscription(identifier=identifier)

    @app.tool()
    async def update_delivery_subscription(identifier: str, payload: dict[str, Any] | None = None) -> str:
        """Update one normalized delivery subscription."""
        return await _run_update_delivery_subscription(identifier=identifier, payload=payload)

    @app.tool()
    async def delete_delivery_subscription(identifier: str) -> str:
        """Delete one normalized delivery subscription."""
        return await _run_delete_delivery_subscription(identifier=identifier)

    @app.tool()
    async def list_delivery_dispatch_records(
        limit: int = 20,
        status: str | None = None,
        subscription_id: str | None = None,
        subject_kind: str | None = None,
        subject_ref: str | None = None,
        output_kind: str | None = None,
        route_name: str | None = None,
    ) -> str:
        """List attributable delivery dispatch records created from route-backed report dispatch."""
        return await _run_list_delivery_dispatch_records(
            limit=limit,
            status=status,
            subscription_id=subscription_id,
            subject_kind=subject_kind,
            subject_ref=subject_ref,
            output_kind=output_kind,
            route_name=route_name,
        )

    @app.tool()
    async def build_report_delivery_package(subscription_identifier: str, profile_id: str | None = None) -> str:
        """Build one deterministic report delivery package for a report subscription."""
        return await _run_build_report_delivery_package(
            subscription_identifier=subscription_identifier,
            profile_id=profile_id,
        )

    @app.tool()
    async def dispatch_report_delivery(subscription_identifier: str, profile_id: str | None = None) -> str:
        """Dispatch one report subscription through its named delivery routes and persist dispatch records."""
        return await _run_dispatch_report_delivery(
            subscription_identifier=subscription_identifier,
            profile_id=profile_id,
        )

    @app.tool()
    async def mark_processed(item_id: str, processed: bool = True) -> str:  # noqa: ANN001
        return await _run_mark_processed(item_id, processed=processed)

    @app.tool()
    async def query_unprocessed(limit: int = 20, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        return await _run_query_unprocessed(limit=limit, min_confidence=min_confidence)

    @app.tool()
    async def triage_list(
        limit: int = 20,
        min_confidence: float = 0.0,
        states: list[str] | None = None,
        include_closed: bool = False,
    ) -> str:  # noqa: ANN001
        """List triage queue items from the inbox."""
        return await _run_triage_list(
            limit=limit,
            min_confidence=min_confidence,
            states=states,
            include_closed=include_closed,
        )

    @app.tool()
    async def triage_update(
        item_id: str,
        state: str,
        note: str = "",
        actor: str = "mcp",
        duplicate_of: str = "",
    ) -> str:  # noqa: ANN001
        """Update triage state for one inbox item."""
        return await _run_triage_update(
            item_id=item_id,
            state=state,
            note=note,
            actor=actor,
            duplicate_of=duplicate_of or None,
        )

    @app.tool()
    async def triage_note(item_id: str, note: str, author: str = "mcp") -> str:  # noqa: ANN001
        """Append one triage note to an inbox item."""
        return await _run_triage_note(item_id=item_id, note=note, author=author)

    @app.tool()
    async def triage_stats(min_confidence: float = 0.0) -> str:  # noqa: ANN001
        """Show triage queue counts by state."""
        return await _run_triage_stats(min_confidence=min_confidence)

    @app.tool()
    async def triage_explain(item_id: str, limit: int = 5) -> str:  # noqa: ANN001
        """Explain likely duplicate candidates for one inbox item."""
        return await _run_triage_explain(item_id=item_id, limit=limit)

    @app.tool()
    async def query_inbox(limit: int = 20, min_confidence: float = 0.0) -> str:  # noqa: ANN001
        reader = DataPulseReader()
        items = reader.list_memory(limit=limit, min_confidence=min_confidence)
        return json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)

    @app.tool()
    async def search_web(
        query: str,
        sites: list[str] | None = None,
        platform: str | None = None,
        limit: int = 5,
        fetch_content: bool = True,
        extract_entities: bool = False,
        entity_mode: str = "fast",
        store_entities: bool = True,
        entity_api_key: str | None = None,
        entity_model: str = "gpt-4o-mini",
        entity_api_base: str = "https://api.openai.com/v1",
        min_confidence: float = 0.0,
        provider: str = "auto",
        mode: str = "single",
        deep: bool = False,
        news: bool = False,
        time_range: str | None = None,
        freshness: str | None = None,
    ) -> str:  # noqa: ANN001
        """Search the web and return scored, LLM-friendly results."""
        return await _run_search_web(
            query=query,
            sites=sites,
            platform=platform,
            limit=limit,
            fetch_content=fetch_content,
            min_confidence=min_confidence,
            provider=provider,
            mode=mode,
            deep=deep,
            news=news,
            time_range=time_range,
            freshness=freshness,
            extract_entities=extract_entities,
            entity_mode=entity_mode,
            store_entities=store_entities,
            entity_api_key=entity_api_key,
            entity_model=entity_model,
            entity_api_base=entity_api_base,
        )

    @app.tool()
    async def extract_entities(
        url: str,
        mode: str = "fast",
        store_entities: bool = True,
        llm_api_key: str | None = None,
        llm_model: str = "gpt-4o-mini",
        llm_api_base: str = "https://api.openai.com/v1",
    ) -> str:
        return await _run_extract_entities(
            url=url,
            mode=mode,
            store_entities=store_entities,
            llm_api_key=llm_api_key,
            llm_model=llm_model,
            llm_api_base=llm_api_base,
        )

    @app.tool()
    async def query_entities(
        entity_type: str = "",
        name: str = "",
        min_sources: int = 1,
        limit: int = 50,
    ) -> str:
        return await _run_query_entities(
            entity_type=entity_type,
            name=name,
            min_sources=min_sources,
            limit=limit,
        )

    @app.tool()
    async def entity_graph(entity_name: str, limit: int = 50) -> str:
        return await _run_entity_graph(entity_name=entity_name, limit=limit)

    @app.tool()
    async def entity_stats() -> str:
        return await _run_entity_stats()

    @app.tool()
    async def read_url_advanced(
        url: str,
        target_selector: str = "",
        wait_for_selector: str = "",
        no_cache: bool = False,
        with_alt: bool = False,
        min_confidence: float = 0.0,
    ) -> str:  # noqa: ANN001
        """Read a URL with CSS selector targeting and advanced options."""
        return await _run_read_url_advanced(
            url=url,
            target_selector=target_selector,
            wait_for_selector=wait_for_selector,
            no_cache=no_cache,
            with_alt=with_alt,
            min_confidence=min_confidence,
        )

    @app.tool()
    async def trending(
        location: str = "",
        top_n: int = 20,
        store: bool = False,
        validate: bool = False,
        validate_mode: str = "strict",
    ) -> str:  # noqa: ANN001
        """Get trending topics on X/Twitter for a location (powered by trends24.in)."""
        return await _run_trending(
            location=location,
            top_n=top_n,
            store=store,
            validate=validate,
            validate_mode=validate_mode,
        )

    @app.tool()
    async def doctor() -> str:  # noqa: ANN001
        """Run health checks on all collectors, grouped by tier."""
        return await _run_doctor()

    @app.tool()
    async def detect_platform(url: str) -> str:  # noqa: ANN001
        reader = DataPulseReader()
        return reader.detect_platform(url)

    @app.tool()
    async def health() -> str:
        import sys
        import time

        import datapulse

        reader = DataPulseReader()
        return json.dumps(
            {
                "ok": True,
                "version": datapulse.__version__,
                "python_version": sys.version.split()[0],
                "uptime_seconds": round(time.monotonic(), 1),
                "parsers": reader.router.available_parsers,
                "stored": len(reader.inbox.items),
            },
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        app: Any = _LocalMCP("datapulse")
    else:
        app = FastMCP("datapulse")

    _register_tools(app)
    app.run()
