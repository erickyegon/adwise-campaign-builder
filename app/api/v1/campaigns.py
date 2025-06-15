"""
Campaign Management API Endpoints

This module implements the campaign management endpoints as specified in the LDL:
- Create campaign (POST /campaigns)
- List campaigns (GET /campaigns)
- Get campaign (GET /campaigns/{id})
- Update campaign (PUT /campaigns/{id})
- Delete campaign (DELETE /campaigns/{id})
- Campaign collaboration endpoints
- Campaign analytics integration

Implements the exact LDL algorithm:
function createCampaign(userId, campaignInput):
    validateUser(userId)
    campaign = new Campaign(campaignInput)
    for each adSpec in campaignInput.ads:
        adCopy = AIService.generateCopy(adSpec)
        adVisual = AIService.generateVisual(adSpec)
        ad = new Ad(adCopy, adVisual, adSpec.channel)
        campaign.addAd(ad)
    save campaign to DB
    return campaign
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from beanie.operators import In, And, Or

from app.models.mongodb_models import Campaign, Ad, User, Team, CampaignStatus, AdType, AdChannel
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    AdSpecification, CampaignWithAds, CampaignCollaboratorAdd
)
from app.services.langchain_service import get_langchain_service, CampaignGenerationRequest
from app.integrations.euri import get_euri_client
from app.api.deps import get_current_user, get_database
from app.core.database.mongodb import get_db
from app.tasks.campaign_tasks import generate_campaign_content_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> CampaignResponse:
    """
    Create new campaign with AI-generated content (LDL Algorithm Implementation)
    
    Implements the exact LDL createCampaign algorithm:
    1. Validate user
    2. Create campaign
    3. Generate AI content for each ad specification
    4. Save to database
    """
    try:
        # Step 1: Validate user (already done by get_current_user dependency)
        logger.info(f"Creating campaign for user {current_user.id}")
        
        # Step 2: Create campaign object
        campaign = Campaign(
            name=campaign_data.name,
            description=campaign_data.description,
            owner_id=str(current_user.id),
            team_id=campaign_data.team_id,
            objective=campaign_data.objective,
            target_audience=campaign_data.target_audience,
            budget=campaign_data.budget,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            status=CampaignStatus.DRAFT,
            ai_settings=campaign_data.ai_settings or {}
        )
        
        # Save campaign first to get ID
        await campaign.insert()
        
        # Step 3: Generate AI content for each ad specification (LDL Algorithm)
        if campaign_data.ad_specifications:
            await generate_ads_for_campaign(
                campaign, 
                campaign_data.ad_specifications, 
                background_tasks
            )
        
        # Step 4: Save campaign with ads to DB
        await campaign.save()
        
        # Add audit entry
        campaign.add_audit_entry(
            action="create",
            user_id=current_user.id,
            changes={"status": "created"},
            metadata={"ad_count": len(campaign_data.ad_specifications or [])}
        )
        await campaign.save()
        
        logger.info(f"Campaign {campaign.id} created successfully")
        
        return CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            description=campaign.description,
            owner_id=campaign.owner_id,
            team_id=campaign.team_id,
            status=campaign.status,
            objective=campaign.objective,
            target_audience=campaign.target_audience,
            budget=campaign.budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            ads_count=len(campaign.ads) if campaign.ads else 0
        )
        
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create campaign: {str(e)}"
        )


async def generate_ads_for_campaign(
    campaign: Campaign,
    ad_specifications: List[AdSpecification],
    background_tasks: BackgroundTasks
) -> None:
    """
    Generate AI content for campaign ads (LDL Algorithm Implementation)
    
    For each adSpec in campaignInput.ads:
        adCopy = AIService.generateCopy(adSpec)
        adVisual = AIService.generateVisual(adSpec)
        ad = new Ad(adCopy, adVisual, adSpec.channel)
        campaign.addAd(ad)
    """
    try:
        euri_client = await get_euri_client()
        
        for ad_spec in ad_specifications:
            logger.info(f"Generating ad content for {ad_spec.channel}")
            
            # Generate ad copy using AI Service (LDL: adCopy = AIService.generateCopy(adSpec))
            copy_response = await euri_client.generate_copy(
                prompt=ad_spec.content_brief,
                ad_type=ad_spec.type,
                channel=ad_spec.channel,
                target_audience=campaign.target_audience,
                brand_guidelines=campaign.ai_settings.get('brand_guidelines'),
                max_length=ad_spec.max_length or 300
            )
            
            # Generate visual description (LDL: adVisual = AIService.generateVisual(adSpec))
            visual_response = await euri_client.generate_visual_description(
                description=ad_spec.visual_brief or f"Visual for {ad_spec.type} ad",
                style=ad_spec.visual_style or "modern",
                dimensions=ad_spec.dimensions or {"width": 1200, "height": 628},
                brand_colors=campaign.ai_settings.get('brand_colors')
            )
            
            # Create ad object (LDL: ad = new Ad(adCopy, adVisual, adSpec.channel))
            ad = Ad(
                campaign_id=str(campaign.id),
                type=AdType(ad_spec.type),
                channel=AdChannel(ad_spec.channel),
                headline=ad_spec.headline,
                copy=copy_response.get('content', ''),
                description=visual_response.get('visual_description', ''),
                visual_url=None,  # Will be generated later
                status=ad_spec.status or "draft",
                ai_generated=True,
                ai_generation_params={
                    "content_model": copy_response.get('model'),
                    "visual_model": visual_response.get('model'),
                    "generation_time": datetime.now().isoformat()
                }
            )
            
            # Save ad
            await ad.insert()
            
            # Add to campaign (LDL: campaign.addAd(ad))
            if not campaign.ads:
                campaign.ads = []
            campaign.ads.append(ad)
            
            logger.info(f"Generated ad {ad.id} for campaign {campaign.id}")
        
        # Schedule background task for additional processing
        background_tasks.add_task(
            generate_campaign_content_task,
            str(campaign.id),
            [spec.dict() for spec in ad_specifications]
        )
        
    except Exception as e:
        logger.error(f"Error generating ads for campaign {campaign.id}: {e}")
        raise


@router.get("/", response_model=CampaignListResponse)
async def list_campaigns(
    skip: int = Query(0, ge=0, description="Number of campaigns to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of campaigns to return"),
    status: Optional[CampaignStatus] = Query(None, description="Filter by campaign status"),
    team_id: Optional[str] = Query(None, description="Filter by team ID"),
    search: Optional[str] = Query(None, description="Search in campaign names and descriptions"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> CampaignListResponse:
    """
    List campaigns with filtering and pagination
    
    Returns campaigns that the user has access to based on:
    - Campaigns they own
    - Campaigns from their teams
    - Campaigns they collaborate on
    """
    try:
        # Build query filters
        filters = []
        
        # User access filter (owner, team member, or collaborator)
        user_access_filter = Or(
            Campaign.owner_id == str(current_user.id),
            Campaign.team_id.in_(current_user.team_ids),
            Campaign.collaborators.user_id == str(current_user.id)
        )
        filters.append(user_access_filter)
        
        # Status filter
        if status:
            filters.append(Campaign.status == status)
        
        # Team filter
        if team_id:
            filters.append(Campaign.team_id == team_id)
        
        # Search filter
        if search:
            search_filter = Or(
                Campaign.name.contains(search, case_insensitive=True),
                Campaign.description.contains(search, case_insensitive=True)
            )
            filters.append(search_filter)
        
        # Execute query
        query = Campaign.find(And(*filters))
        
        # Get total count
        total = await query.count()
        
        # Get paginated results
        campaigns = await query.skip(skip).limit(limit).sort(-Campaign.created_at).to_list()
        
        # Convert to response format
        campaign_responses = [
            CampaignResponse(
                id=str(campaign.id),
                name=campaign.name,
                description=campaign.description,
                owner_id=campaign.owner_id,
                team_id=campaign.team_id,
                status=campaign.status,
                objective=campaign.objective,
                target_audience=campaign.target_audience,
                budget=campaign.budget,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                ads_count=len(campaign.ads) if campaign.ads else 0
            )
            for campaign in campaigns
        ]
        
        return CampaignListResponse(
            campaigns=campaign_responses,
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list campaigns: {str(e)}"
        )


@router.get("/{campaign_id}", response_model=CampaignWithAds)
async def get_campaign(
    campaign_id: str,
    include_ads: bool = Query(True, description="Include ads in response"),
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> CampaignWithAds:
    """
    Get campaign by ID with optional ads inclusion
    """
    try:
        # Find campaign
        campaign = await Campaign.get(PydanticObjectId(campaign_id))
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check access permissions
        if not await user_has_campaign_access(current_user, campaign):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this campaign"
            )
        
        # Get ads if requested
        ads = []
        if include_ads:
            ads = await Ad.find(Ad.campaign_id == str(campaign.id)).to_list()
        
        return CampaignWithAds(
            id=str(campaign.id),
            name=campaign.name,
            description=campaign.description,
            owner_id=campaign.owner_id,
            team_id=campaign.team_id,
            status=campaign.status,
            objective=campaign.objective,
            target_audience=campaign.target_audience,
            budget=campaign.budget,
            budget_allocation=campaign.budget_allocation,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            ai_settings=campaign.ai_settings,
            collaborators=campaign.collaborators,
            performance_summary=campaign.performance_summary,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            ads=[
                {
                    "id": str(ad.id),
                    "type": ad.type,
                    "channel": ad.channel,
                    "headline": ad.headline,
                    "copy": ad.copy,
                    "description": ad.description,
                    "visual_url": ad.visual_url,
                    "status": ad.status,
                    "ai_generated": ad.ai_generated,
                    "created_at": ad.created_at,
                    "updated_at": ad.updated_at
                }
                for ad in ads
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get campaign: {str(e)}"
        )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
) -> CampaignResponse:
    """
    Update campaign with change tracking for collaboration
    """
    try:
        # Find campaign
        campaign = await Campaign.get(PydanticObjectId(campaign_id))
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check edit permissions
        if not await user_can_edit_campaign(current_user, campaign):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No edit permission for this campaign"
            )
        
        # Track changes for collaboration
        changes = {}
        update_data = campaign_update.dict(exclude_unset=True)
        
        for field, new_value in update_data.items():
            old_value = getattr(campaign, field, None)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
                setattr(campaign, field, new_value)
        
        if changes:
            # Update timestamps and version
            campaign.updated_at = datetime.now()
            campaign.version += 1
            
            # Add change entry for real-time collaboration
            campaign.add_change_entry(
                user_id=current_user.id,
                change_type="update",
                details=changes
            )
            
            # Add audit entry
            campaign.add_audit_entry(
                action="update",
                user_id=current_user.id,
                changes=changes
            )
            
            await campaign.save()
            
            logger.info(f"Campaign {campaign_id} updated by user {current_user.id}")
        
        return CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            description=campaign.description,
            owner_id=campaign.owner_id,
            team_id=campaign.team_id,
            status=campaign.status,
            objective=campaign.objective,
            target_audience=campaign.target_audience,
            budget=campaign.budget,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            ads_count=len(campaign.ads) if campaign.ads else 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update campaign: {str(e)}"
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete campaign (soft delete with audit trail)
    """
    try:
        # Find campaign
        campaign = await Campaign.get(PydanticObjectId(campaign_id))
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Check delete permissions (only owner or admin)
        if campaign.owner_id != str(current_user.id) and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only campaign owner or admin can delete campaigns"
            )
        
        # Soft delete
        campaign.soft_delete(current_user.id)
        campaign.add_audit_entry(
            action="delete",
            user_id=current_user.id,
            changes={"deleted": True}
        )
        
        await campaign.save()
        
        # Also soft delete associated ads
        ads = await Ad.find(Ad.campaign_id == str(campaign.id)).to_list()
        for ad in ads:
            ad.soft_delete(current_user.id)
            await ad.save()
        
        logger.info(f"Campaign {campaign_id} deleted by user {current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting campaign {campaign_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete campaign: {str(e)}"
        )


# Helper functions
async def user_has_campaign_access(user: User, campaign: Campaign) -> bool:
    """Check if user has access to campaign"""
    # Owner access
    if campaign.owner_id == str(user.id):
        return True
    
    # Team access
    if campaign.team_id and campaign.team_id in user.team_ids:
        return True
    
    # Collaborator access
    if campaign.collaborators:
        for collaborator in campaign.collaborators:
            if collaborator.user_id == str(user.id):
                return True
    
    # Admin access
    if user.role == "admin":
        return True
    
    return False


async def user_can_edit_campaign(user: User, campaign: Campaign) -> bool:
    """Check if user can edit campaign"""
    # Owner can edit
    if campaign.owner_id == str(user.id):
        return True
    
    # Admin can edit
    if user.role == "admin":
        return True
    
    # Collaborator with edit permission
    if campaign.collaborators:
        for collaborator in campaign.collaborators:
            if (collaborator.user_id == str(user.id) and 
                collaborator.role in ["editor", "admin"]):
                return True
    
    return False
