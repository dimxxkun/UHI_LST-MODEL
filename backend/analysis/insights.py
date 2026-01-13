"""
Insights Generator Module

This module generates natural language explanations and actionable 
recommendations based on UHI/LST analysis results.

The insights are designed to be:
- Clear and understandable by non-technical stakeholders
- Actionable with specific mitigation strategies
- Prioritized based on severity and impact

References:
- EPA Heat Island Mitigation Guidelines
- WHO Urban Health Guidelines
- IPCC Climate Adaptation Strategies
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Any, Optional, Tuple
import math


class UHISeverity(IntEnum):
    """UHI severity levels for insight generation."""
    MINIMAL = 0
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    CRITICAL = 4


class Priority(IntEnum):
    """Recommendation priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Recommendation:
    """A prioritized recommendation with details."""
    title: str
    description: str
    priority: Priority
    category: str  # e.g., "Green Infrastructure", "Building Materials", "Policy"
    timeframe: str  # e.g., "Immediate", "Short-term", "Long-term"
    estimated_impact: str  # e.g., "High", "Medium", "Low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "priority_value": int(self.priority),
            "category": self.category,
            "timeframe": self.timeframe,
            "estimated_impact": self.estimated_impact,
        }


# Severity thresholds
UHI_SEVERITY_THRESHOLDS = {
    UHISeverity.MINIMAL: 1.0,
    UHISeverity.MILD: 3.0,
    UHISeverity.MODERATE: 5.0,
    UHISeverity.SEVERE: 7.0,
    UHISeverity.CRITICAL: float('inf'),
}

SEVERITY_DESCRIPTIONS = {
    UHISeverity.MINIMAL: "minimal",
    UHISeverity.MILD: "mild",
    UHISeverity.MODERATE: "moderate",
    UHISeverity.SEVERE: "severe",
    UHISeverity.CRITICAL: "critical",
}


def classify_uhi_severity(intensity: float) -> UHISeverity:
    """Classify UHI intensity into severity levels."""
    if intensity < UHI_SEVERITY_THRESHOLDS[UHISeverity.MINIMAL]:
        return UHISeverity.MINIMAL
    elif intensity < UHI_SEVERITY_THRESHOLDS[UHISeverity.MILD]:
        return UHISeverity.MILD
    elif intensity < UHI_SEVERITY_THRESHOLDS[UHISeverity.MODERATE]:
        return UHISeverity.MODERATE
    elif intensity < UHI_SEVERITY_THRESHOLDS[UHISeverity.SEVERE]:
        return UHISeverity.SEVERE
    else:
        return UHISeverity.CRITICAL


def get_health_impact_description(severity: UHISeverity) -> str:
    """Get health impact description based on severity."""
    impacts = {
        UHISeverity.MINIMAL: (
            "Current conditions pose minimal additional health risk from urban heat. "
            "Standard precautions for vulnerable populations are sufficient."
        ),
        UHISeverity.MILD: (
            "Mild heat stress may affect sensitive individuals including the elderly, "
            "young children, and those with pre-existing conditions. Increased hydration "
            "and limited outdoor activity during peak hours is recommended."
        ),
        UHISeverity.MODERATE: (
            "Moderate heat stress conditions present. Risk of heat-related illness is elevated, "
            "particularly in areas without adequate cooling. Outdoor workers and athletic "
            "activities should take additional precautions."
        ),
        UHISeverity.SEVERE: (
            "Severe heat conditions detected. Significant health risks exist for the general "
            "population. Heat exhaustion and heat stroke cases are likely to increase. "
            "Emergency cooling centers should be activated."
        ),
        UHISeverity.CRITICAL: (
            "CRITICAL: Extreme heat emergency conditions. Life-threatening heat exposure is "
            "possible without adequate cooling. Immediate protective actions are required "
            "including public health alerts and emergency response activation."
        ),
    }
    return impacts.get(severity, "")


def generate_explanation(
    uhi_result: Dict[str, Any],
    land_cover_stats: Dict[str, Any],
    ndvi_stats: Dict[str, Any],
    lst_stats: Dict[str, Any],
) -> str:
    """
    Generate a natural language explanation of the analysis results.
    
    Args:
        uhi_result: Results from analyze_uhi()
        land_cover_stats: Results from get_land_cover_statistics()
        ndvi_stats: Results from get_ndvi_statistics()
        lst_stats: Results from get_lst_statistics()
    
    Returns:
        A comprehensive natural language explanation string
    """
    sections = []
    
    # Extract key metrics
    uhi_intensity = uhi_result.get("uhi_intensity")
    urban_mean = uhi_result.get("urban_mean_temp")
    rural_mean = uhi_result.get("rural_mean_temp")
    hotspot_count = uhi_result.get("hotspot_count", 0)
    affected_area = uhi_result.get("affected_area_km2", 0)
    
    # Land cover percentages
    lc_percentages = land_cover_stats.get("class_percentages", {})
    urban_pct = lc_percentages.get("Urban/Built-up", 0)
    vegetation_pct = lc_percentages.get("Vegetation", 0)
    water_pct = lc_percentages.get("Water", 0)
    
    # NDVI stats
    mean_ndvi = ndvi_stats.get("mean")
    
    # LST stats
    max_temp = lst_stats.get("max")
    min_temp = lst_stats.get("min")
    mean_temp = lst_stats.get("mean")
    
    # ========== Section 1: Overview ==========
    if uhi_intensity is not None:
        severity = classify_uhi_severity(uhi_intensity)
        severity_desc = SEVERITY_DESCRIPTIONS[severity]
        
        overview = f"""## Urban Heat Island Analysis Summary

The analysis reveals a **{severity_desc} Urban Heat Island (UHI) effect** with an intensity of **{uhi_intensity:.1f}°C**. 

Urban areas exhibit a mean temperature of **{urban_mean:.1f}°C**, which is {abs(uhi_intensity):.1f}°C {"warmer" if uhi_intensity > 0 else "cooler"} than surrounding vegetated (rural reference) areas at **{rural_mean:.1f}°C**."""
        sections.append(overview)
    
    # ========== Section 2: Temperature Analysis ==========
    if max_temp is not None and min_temp is not None:
        temp_range = max_temp - min_temp
        temp_section = f"""### Temperature Distribution

Surface temperatures range from **{min_temp:.1f}°C to {max_temp:.1f}°C**, with a spatial variation of {temp_range:.1f}°C across the study area. The mean surface temperature is **{mean_temp:.1f}°C**."""
        
        if hotspot_count > 0:
            temp_section += f"""

**{hotspot_count:,} thermal hotspot pixels** were identified, covering approximately **{affected_area:.2f} km²** of land area. These hotspots represent locations where temperatures exceed the regional mean by more than 2 standard deviations."""
        
        sections.append(temp_section)
    
    # ========== Section 3: Land Cover Analysis ==========
    land_cover_section = f"""### Land Cover Composition

The study area contains:
- **{urban_pct:.1f}%** urban/built-up surfaces
- **{vegetation_pct:.1f}%** vegetation cover
- **{water_pct:.1f}%** water bodies"""
    
    if urban_pct > 60:
        land_cover_section += f"""

⚠️ **High Urban Density Alert**: With more than 60% impervious surface coverage, this area is highly susceptible to heat accumulation. Urban surfaces absorb and retain solar radiation, contributing significantly to elevated temperatures."""
    elif urban_pct > 40:
        land_cover_section += f"""

The urban coverage is moderately high. As impervious surfaces continue to expand, UHI effects are likely to intensify without mitigation measures."""
    
    sections.append(land_cover_section)
    
    # ========== Section 4: Vegetation Health ==========
    if mean_ndvi is not None:
        if mean_ndvi < 0.2:
            veg_health = "poor"
            veg_detail = "indicating minimal healthy vegetation cover"
        elif mean_ndvi < 0.3:
            veg_health = "fair"
            veg_detail = "suggesting sparse or stressed vegetation"
        elif mean_ndvi < 0.5:
            veg_health = "moderate"
            veg_detail = "with mixed vegetation conditions"
        else:
            veg_health = "good"
            veg_detail = "indicating healthy, dense vegetation"
        
        veg_section = f"""### Vegetation Health

The mean NDVI value of **{mean_ndvi:.2f}** indicates **{veg_health}** vegetation health across the study area, {veg_detail}. Vegetation plays a critical role in urban cooling through evapotranspiration and shading."""
        
        if mean_ndvi < 0.3:
            veg_section += """

🌱 **Low Vegetation Alert**: The limited vegetation cover reduces the natural cooling capacity of the area. Green infrastructure investments would provide significant temperature reduction benefits."""
        
        sections.append(veg_section)
    
    # ========== Section 5: Health Impact Assessment ==========
    if uhi_intensity is not None:
        severity = classify_uhi_severity(uhi_intensity)
        health_impact = get_health_impact_description(severity)
        
        health_section = f"""### Health Impact Assessment

{health_impact}"""
        sections.append(health_section)
    
    return "\n\n".join(sections)


def generate_recommendations(
    uhi_result: Dict[str, Any],
    land_cover_stats: Dict[str, Any],
    ndvi_stats: Dict[str, Any],
    lst_stats: Dict[str, Any],
    max_recommendations: int = 5,
) -> List[Recommendation]:
    """
    Generate prioritized recommendations based on analysis results.
    
    Args:
        uhi_result: Results from analyze_uhi()
        land_cover_stats: Results from get_land_cover_statistics()
        ndvi_stats: Results from get_ndvi_statistics()
        lst_stats: Results from get_lst_statistics()
        max_recommendations: Maximum number of recommendations to return
    
    Returns:
        List of Recommendation objects, sorted by priority
    """
    recommendations = []
    
    # Extract metrics
    uhi_intensity = uhi_result.get("uhi_intensity", 0) or 0
    hotspot_count = uhi_result.get("hotspot_count", 0)
    affected_area = uhi_result.get("affected_area_km2", 0)
    
    lc_percentages = land_cover_stats.get("class_percentages", {})
    urban_pct = lc_percentages.get("Urban/Built-up", 0)
    vegetation_pct = lc_percentages.get("Vegetation", 0)
    
    mean_ndvi = ndvi_stats.get("mean", 0.5) or 0.5
    max_temp = lst_stats.get("max", 35) or 35
    
    # ========== Critical: Severe UHI (>5°C) ==========
    if uhi_intensity > 5:
        recommendations.append(Recommendation(
            title="Activate Emergency Cooling Measures",
            description=(
                f"With a UHI intensity of {uhi_intensity:.1f}°C, immediate action is required. "
                "Open cooling centers in affected neighborhoods, extend public facility hours, "
                "and deploy mobile cooling units to vulnerable areas. Issue public health advisories "
                "recommending reduced outdoor activity during peak heat hours (11 AM - 4 PM)."
            ),
            priority=Priority.CRITICAL,
            category="Emergency Response",
            timeframe="Immediate",
            estimated_impact="High",
        ))
        
        recommendations.append(Recommendation(
            title="Implement Cool Pavement Program",
            description=(
                "Apply high-albedo coatings or reflective surfaces to roads and parking lots "
                "in identified hotspot areas. Cool pavement technologies can reduce surface "
                "temperatures by 10-20°C compared to traditional asphalt, directly mitigating "
                "UHI effects in severely affected zones."
            ),
            priority=Priority.HIGH,
            category="Infrastructure",
            timeframe="Short-term (3-6 months)",
            estimated_impact="High",
        ))
    
    # ========== High Urban Coverage (>60%) ==========
    if urban_pct > 60:
        recommendations.append(Recommendation(
            title="Expand Urban Tree Canopy Program",
            description=(
                f"Urban areas cover {urban_pct:.1f}% of the study area. Implement an aggressive "
                "tree planting program targeting 40% canopy coverage in residential and commercial "
                "zones. Prioritize shade trees along pedestrian corridors, parking lots, and around "
                "buildings. Each 10% increase in tree canopy can reduce ambient temperatures by 1-2°C."
            ),
            priority=Priority.HIGH,
            category="Green Infrastructure",
            timeframe="Long-term (2-5 years)",
            estimated_impact="High",
        ))
        
        recommendations.append(Recommendation(
            title="Mandate Green Building Standards",
            description=(
                "Require cool roofs (high Solar Reflectance Index) and green roofs for new "
                "construction and major renovations. Cool roofs can reduce surface temperatures "
                "by up to 30°C compared to dark roofs. Offer tax incentives for voluntary retrofits."
            ),
            priority=Priority.MEDIUM,
            category="Policy",
            timeframe="Medium-term (1-2 years)",
            estimated_impact="Medium",
        ))
    
    # ========== Low NDVI (<0.3) ==========
    if mean_ndvi < 0.3:
        recommendations.append(Recommendation(
            title="Invest in Green Infrastructure Network",
            description=(
                f"Mean NDVI of {mean_ndvi:.2f} indicates insufficient vegetation for effective "
                "cooling. Develop a connected green infrastructure network including pocket parks, "
                "green corridors, bioswales, and urban gardens. Target conversion of 5% of "
                "impervious surfaces to vegetated areas within identified hotspot zones."
            ),
            priority=Priority.HIGH,
            category="Green Infrastructure",
            timeframe="Medium-term (1-3 years)",
            estimated_impact="High",
        ))
        
        recommendations.append(Recommendation(
            title="Establish Community Garden Program",
            description=(
                "Convert vacant lots and underutilized spaces in heat-vulnerable neighborhoods "
                "into community gardens. This provides both cooling benefits and community "
                "resilience through local food production. Target 5 new community gardens "
                "per high-impact area."
            ),
            priority=Priority.MEDIUM,
            category="Community",
            timeframe="Short-term (6-12 months)",
            estimated_impact="Medium",
        ))
    
    # ========== Significant Hotspots ==========
    if hotspot_count > 1000 or affected_area > 1.0:
        recommendations.append(Recommendation(
            title="Target Hotspot Mitigation Zones",
            description=(
                f"Approximately {affected_area:.2f} km² has been identified as thermal hotspots. "
                "Prioritize these areas for immediate interventions including shade structures, "
                "misting systems, and reflective surface treatments. Create detailed micro-climate "
                "improvement plans for the top 10 most critical hotspot clusters."
            ),
            priority=Priority.HIGH,
            category="Targeted Intervention",
            timeframe="Short-term (3-6 months)",
            estimated_impact="High",
        ))
    
    # ========== Moderate conditions ==========
    if uhi_intensity > 3 and uhi_intensity <= 5:
        recommendations.append(Recommendation(
            title="Develop Heat Action Plan",
            description=(
                f"The moderate UHI intensity of {uhi_intensity:.1f}°C warrants a comprehensive "
                "heat action plan. Establish early warning systems, identify vulnerable populations, "
                "and create neighborhood-level response protocols. Train community health workers "
                "on heat illness prevention and response."
            ),
            priority=Priority.MEDIUM,
            category="Planning",
            timeframe="Medium-term (6-12 months)",
            estimated_impact="Medium",
        ))
    
    # ========== Water features ==========
    if uhi_intensity > 3 and vegetation_pct < 30:
        recommendations.append(Recommendation(
            title="Integrate Blue Infrastructure",
            description=(
                "Incorporate water features such as fountains, splash pads, and urban streams "
                "in high-traffic public spaces. Water bodies and evaporative cooling features "
                "can reduce local temperatures by 2-4°C. Prioritize locations near transit stops "
                "and community gathering spaces."
            ),
            priority=Priority.MEDIUM,
            category="Blue Infrastructure",
            timeframe="Medium-term (1-2 years)",
            estimated_impact="Medium",
        ))
    
    # ========== General (always include at least one) ==========
    if len(recommendations) < 3:
        recommendations.append(Recommendation(
            title="Establish Long-term Monitoring Program",
            description=(
                "Implement continuous thermal monitoring using satellite imagery and ground-based "
                "sensors. Track UHI trends seasonally and evaluate mitigation effectiveness. "
                "Create public dashboards showing real-time heat conditions and historical trends."
            ),
            priority=Priority.LOW,
            category="Monitoring",
            timeframe="Ongoing",
            estimated_impact="Low",
        ))
    
    # Sort by priority (highest first) and limit
    recommendations.sort(key=lambda r: r.priority, reverse=True)
    return recommendations[:max_recommendations]


def generate_insights(
    uhi_result: Dict[str, Any],
    land_cover_stats: Dict[str, Any],
    ndvi_stats: Dict[str, Any],
    lst_stats: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate comprehensive insights including explanation and recommendations.
    
    This is the main entry point for insight generation.
    
    Args:
        uhi_result: Results from analyze_uhi()
        land_cover_stats: Results from get_land_cover_statistics()
        ndvi_stats: Results from get_ndvi_statistics()
        lst_stats: Results from get_lst_statistics()
    
    Returns:
        Dictionary containing:
        - explanation: Natural language explanation string
        - recommendations: List of Recommendation dicts
        - severity: UHI severity level
        - summary_metrics: Key metrics for quick reference
    """
    # Generate explanation
    explanation = generate_explanation(
        uhi_result, land_cover_stats, ndvi_stats, lst_stats
    )
    
    # Generate recommendations
    recommendations = generate_recommendations(
        uhi_result, land_cover_stats, ndvi_stats, lst_stats
    )
    
    # Determine overall severity
    uhi_intensity = uhi_result.get("uhi_intensity", 0) or 0
    severity = classify_uhi_severity(uhi_intensity)
    
    # Create summary metrics
    lc_percentages = land_cover_stats.get("class_percentages", {})
    
    summary_metrics = {
        "uhi_intensity_c": uhi_intensity,
        "uhi_severity": SEVERITY_DESCRIPTIONS[severity],
        "urban_coverage_pct": lc_percentages.get("Urban/Built-up", 0),
        "vegetation_coverage_pct": lc_percentages.get("Vegetation", 0),
        "mean_ndvi": ndvi_stats.get("mean"),
        "max_temperature_c": lst_stats.get("max"),
        "mean_temperature_c": lst_stats.get("mean"),
        "hotspot_area_km2": uhi_result.get("affected_area_km2", 0),
        "hotspot_clusters": uhi_result.get("hotspot_cluster_count", 0),
    }
    
    return {
        "explanation": explanation,
        "recommendations": [r.to_dict() for r in recommendations],
        "recommendation_count": len(recommendations),
        "severity": SEVERITY_DESCRIPTIONS[severity],
        "severity_value": int(severity),
        "summary_metrics": summary_metrics,
    }
