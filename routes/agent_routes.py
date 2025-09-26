# agent_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database import models
from schemas.agent_schema import CompanyProfile
from workflow.initial_graph import content_graph, ContentWorkflowState
from integrations.company_info import get_company_profile
from utils.generate_uuid import generate_uuid
import uuid
from datetime import datetime

router = APIRouter(prefix="/agent", tags=["agent_routes"])


async def save_workflow_results(
        db: Session,
        company_id: uuid.UUID,
        final_state: dict
) -> models.WorkflowRun:
    """Save workflow results to database"""
    try:
        # Create workflow run record
        workflow_run = models.WorkflowRun(
            id=generate_uuid(),
            company_id=company_id,
            workflow_id=f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(company_id)[:8]}",

        status="completed" if not final_state.get("error") else "failed",
            completed_at=datetime.utcnow(),
            trends_found=len(final_state["trends"].trending_topics) if final_state["trends"] else 0,
            strategy_created=bool(final_state["strategy"]),
            briefs_generated=final_state["briefs"].total_briefs_generated if final_state["briefs"] else 0,
            error_message=final_state.get("error")
        )

        db.add(workflow_run)
        db.commit()
        db.refresh(workflow_run)

        # Save trending topics
        if final_state["trends"] and final_state["trends"].trending_topics:
            for topic in final_state["trends"].trending_topics:
                trending_topic = models.TrendingTopicResult(
                    id=generate_uuid(),
                    workflow_run_id=workflow_run.id,
                    company_id=company_id,
                    topic=topic.topic,
                    trend_score=topic.trend_score,
                    source=topic.source,
                    relevance_reason=topic.relevance_reason,
                    content_angle=topic.content_angle,
                    business_relevance_score=topic.business_relevance_score,
                    audience_interest_score=topic.audience_interest_score,
                    content_opportunity_score=topic.content_opportunity_score,
                    trend_momentum_score=topic.trend_momentum_score,
                    recommended_platforms=topic.recommended_platforms,
                    target_keywords=topic.target_keywords,
                    competitor_coverage=topic.competitor_coverage,
                    urgency_level=topic.urgency_level,
                    trend_lifespan_estimate=topic.trend_lifespan_estimate
                )
                db.add(trending_topic)

        # Save content strategy
        if final_state["strategy"]:
            strategy = final_state["strategy"]
            strategy_result = models.ContentStrategyResult(
                id=generate_uuid(),
                workflow_run_id=workflow_run.id,
                company_id=company_id,
                strategy_summary=strategy.strategy_summary,
                weekly_focus=strategy.weekly_focus,
                theme_name=strategy.content_strategy.weekly_theme.theme_name,
                focus_area=strategy.content_strategy.weekly_theme.focus_area,
                key_message=strategy.content_strategy.weekly_theme.key_message,
                target_pain_points=strategy.content_strategy.weekly_theme.target_pain_points,
                supporting_themes=strategy.content_strategy.weekly_theme.supporting_themes,
                educational_percentage=strategy.content_strategy.content_mix.educational_percentage,
                industry_insights_percentage=strategy.content_strategy.content_mix.industry_insights_percentage,
                company_product_percentage=strategy.content_strategy.content_mix.company_product_percentage,
                engagement_community_percentage=strategy.content_strategy.content_mix.engagement_community_percentage,
                priority_topics=strategy.content_strategy.priority_topics,
                target_audience_segments=strategy.content_strategy.target_audience_segments,
                competitive_differentiation=strategy.content_strategy.competitive_differentiation,
                content_calendar_notes=strategy.content_strategy.content_calendar_notes,
                success_metrics=strategy.success_metrics,
                risk_mitigation=strategy.risk_mitigation,
                resource_requirements=strategy.resource_requirements,
                timeline_considerations=strategy.timeline_considerations
            )
            db.add(strategy_result)
            db.commit()
            db.refresh(strategy_result)

            # Save recommended content pieces
            if strategy.recommended_content_pieces:
                for piece in strategy.recommended_content_pieces:
                    content_piece = models.RecommendedContentPiece(
                        id=generate_uuid(),
                        strategy_result_id=strategy_result.id,
                        company_id=company_id,
                        topic=piece.topic,
                        priority_score=piece.priority_score,
                        content_type=piece.content_type,
                        platform=piece.platform,
                        secondary_platforms=piece.secondary_platforms,
                        business_impact_score=piece.business_impact_score,
                        audience_engagement_score=piece.audience_engagement_score,
                        competitive_advantage_score=piece.competitive_advantage_score,
                        resource_efficiency_score=piece.resource_efficiency_score,
                        estimated_effort_hours=piece.estimated_effort_hours,
                        target_keywords=piece.target_keywords,
                        related_trends=piece.related_trends,
                        success_probability=piece.success_probability
                    )
                    db.add(content_piece)

        # Save content briefs
        if final_state["briefs"] and final_state["briefs"].content_briefs:
            for brief in final_state["briefs"].content_briefs:
                brief_result = models.ContentBriefResult(
                    id=generate_uuid(),
                    workflow_run_id=workflow_run.id,
                    company_id=company_id,
                    brief_id=brief.brief_id,
                    title=brief.title,
                    final_title_options=brief.final_title_options,
                    objective=brief.objective,
                    target_audience_segment=brief.target_audience_segment,
                    content_type=brief.content_type,
                    platform=brief.platform,
                    content_structure={
                        "hook": brief.content_structure.hook,
                        "main_points": brief.content_structure.main_points,
                        "supporting_details": brief.content_structure.supporting_details,
                        "conclusion": brief.content_structure.conclusion,
                        "call_to_action": brief.content_structure.call_to_action,
                        "content_flow": brief.content_structure.content_flow
                    },
                    seo_optimization={
                        "primary_keyword": brief.seo_optimization.primary_keyword,
                        "secondary_keywords": brief.seo_optimization.secondary_keywords,
                        "meta_description": brief.seo_optimization.meta_description,
                        "title_variations": brief.seo_optimization.title_variations,
                        "target_search_intent": brief.seo_optimization.target_search_intent,
                        "internal_link_opportunities": brief.seo_optimization.internal_link_opportunities,
                        "featured_snippet_optimization": brief.seo_optimization.featured_snippet_optimization
                    },
                    platform_specifications={
                        "optimal_length_words": brief.platform_specifications.optimal_length_words,
                        "optimal_length_characters": brief.platform_specifications.optimal_length_characters,
                        "best_posting_time": brief.platform_specifications.best_posting_time,
                        "hashtags": brief.platform_specifications.hashtags,
                        "visual_requirements": brief.platform_specifications.visual_requirements,
                        "engagement_tactics": brief.platform_specifications.engagement_tactics,
                        "format_specifications": brief.platform_specifications.format_specifications,
                        "cross_promotion_opportunities": brief.platform_specifications.cross_promotion_opportunities
                    },
                    brand_alignment={
                        "tone": brief.brand_alignment.tone,
                        "voice_guidelines": brief.brand_alignment.voice_guidelines,
                        "key_messages": brief.brand_alignment.key_messages,
                        "brand_values_to_highlight": brief.brand_alignment.brand_values_to_highlight,
                        "messaging_restrictions": brief.brand_alignment.messaging_restrictions,
                        "brand_personality_elements": brief.brand_alignment.brand_personality_elements
                    },
                    success_metrics={
                        "primary_kpi": brief.success_metrics.primary_kpi,
                        "target_engagement_rate": brief.success_metrics.target_engagement_rate,
                        "target_reach": brief.success_metrics.target_reach,
                        "target_clicks": brief.success_metrics.target_clicks,
                        "target_leads": brief.success_metrics.target_leads,
                        "target_shares": brief.success_metrics.target_shares,
                        "measurement_timeframe": brief.success_metrics.measurement_timeframe,
                        "benchmark_comparison": brief.success_metrics.benchmark_comparison
                    },
                    execution_notes={
                        "time_estimate_hours": brief.execution_notes.time_estimate_hours,
                        "difficulty_level": brief.execution_notes.difficulty_level,
                        "required_resources": brief.execution_notes.required_resources,
                        "dependencies": brief.execution_notes.dependencies,
                        "review_checkpoints": brief.execution_notes.review_checkpoints,
                        "quality_criteria": brief.execution_notes.quality_criteria,
                        "potential_challenges": brief.execution_notes.potential_challenges
                    },
                    priority_level=brief.priority_level,
                    deadline=datetime.fromisoformat(brief.deadline) if brief.deadline else None,
                    approval_workflow=brief.approval_workflow,
                    strategy_alignment_score=final_state["briefs"].strategy_alignment_score
                )
                db.add(brief_result)

        db.commit()
        return workflow_run

    except Exception as e:
        db.rollback()
        print(f"Error saving workflow results: {str(e)}")
        raise e


@router.post("/run-workflow")
async def run_content_workflow(
        profile: CompanyProfile = Depends(get_company_profile),
        db: Session = Depends(get_db)
):
    """
    Runs the full content workflow for the authenticated user's company.
    """
    try:
        print(f"Starting workflow for company: {profile.company_name}")

        # Build initial state
        state: ContentWorkflowState = {
            "company_id": str(profile.company_id),
            "profile": profile,
            "trends": None,
            "strategy": None,
            "briefs": None,
            "error": None,
            "current_step": "start",
        }

        # Execute the graph (async)
        final_state = await content_graph.ainvoke(state)

        # Save results to database
        try:
            # In run_content_workflow, ensure proper UUID handling
            workflow_run = await save_workflow_results(db, profile.company_id, final_state)
            print(f"Workflow results saved: {workflow_run.workflow_id}")
        except Exception as save_error:
            print(f"Warning: Could not save workflow results: {str(save_error)}")
            # Continue without failing the entire workflow

        # Check if workflow completed successfully
        if final_state.get("error"):
            raise HTTPException(status_code=500, detail=final_state["error"])

        # Return results
        return {
            "status": "success",
            "company_id": final_state["company_id"],
            "current_step": final_state["current_step"],
            "workflow_id": workflow_run.workflow_id if 'workflow_run' in locals() else None,
            "results": {
                "trends_found": len(final_state["trends"].trending_topics) if final_state["trends"] else 0,
                "strategy_created": bool(final_state["strategy"]),
                "briefs_generated": final_state["briefs"].total_briefs_generated if final_state["briefs"] else 0,
            },
            "data": {
                "trends": final_state["trends"].model_dump() if final_state["trends"] else None,
                "strategy": final_state["strategy"].model_dump() if final_state["strategy"] else None,
                "briefs": final_state["briefs"].model_dump() if final_state["briefs"] else None,
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.get("/workflow-history")
async def get_workflow_history(
        profile: CompanyProfile = Depends(get_company_profile),
        db: Session = Depends(get_db)
):
    """Get workflow execution history for the company"""
    try:
        workflow_runs = db.query(models.WorkflowRun).filter(
            models.WorkflowRun.company_id == profile.company_id
        ).order_by(models.WorkflowRun.created_at.desc()).limit(10).all()

        return {
            "status": "success",
            "data": [
                {
                    "workflow_id": run.workflow_id,
                    "status": run.status,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "trends_found": run.trends_found,
                    "strategy_created": run.strategy_created,
                    "briefs_generated": run.briefs_generated,
                    "error_message": run.error_message
                }
                for run in workflow_runs
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow history: {str(e)}")


@router.get("/workflow-results/{workflow_id}")
async def get_workflow_results(
        workflow_id: str,
        profile: CompanyProfile = Depends(get_company_profile),
        db: Session = Depends(get_db)
):
    """Get detailed results for a specific workflow run"""
    try:
        # Get workflow run
        workflow_run = db.query(models.WorkflowRun).filter(
            models.WorkflowRun.workflow_id == workflow_id,
            models.WorkflowRun.company_id == profile.company_id
        ).first()

        if not workflow_run:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Get related data
        trends = db.query(models.TrendingTopicResult).filter(
            models.TrendingTopicResult.workflow_run_id == workflow_run.id
        ).all()

        strategies = db.query(models.ContentStrategyResult).filter(
            models.ContentStrategyResult.workflow_run_id == workflow_run.id
        ).all()

        briefs = db.query(models.ContentBriefResult).filter(
            models.ContentBriefResult.workflow_run_id == workflow_run.id
        ).all()

        return {
            "status": "success",
            "workflow": {
                "workflow_id": workflow_run.workflow_id,
                "status": workflow_run.status,
                "started_at": workflow_run.started_at,
                "completed_at": workflow_run.completed_at,
                "error_message": workflow_run.error_message
            },
            "results": {
                "trends": [
                    {
                        "topic": trend.topic,
                        "trend_score": trend.trend_score,
                        "source": trend.source,
                        "content_angle": trend.content_angle,
                        "recommended_platforms": trend.recommended_platforms,
                        "target_keywords": trend.target_keywords
                    }
                    for trend in trends
                ],
                "strategies": [
                    {
                        "theme_name": strategy.theme_name,
                        "weekly_focus": strategy.weekly_focus,
                        "priority_topics": strategy.priority_topics,
                        "success_metrics": strategy.success_metrics
                    }
                    for strategy in strategies
                ],
                "briefs": [
                    {
                        "brief_id": brief.brief_id,
                        "title": brief.title,
                        "objective": brief.objective,
                        "content_type": brief.content_type,
                        'content':brief.content_structure,
                        "platform": brief.platform,
                        "priority_level": brief.priority_level
                    }
                    for brief in briefs
                ]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving workflow results: {str(e)}")