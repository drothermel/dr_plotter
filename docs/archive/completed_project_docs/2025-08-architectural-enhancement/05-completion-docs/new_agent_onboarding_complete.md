# Complete New Agent Onboarding Guide
## DR_PLOTTER Architectural Enhancement Project - Current State

### **Reading Priority: Essential Files in Order**

#### **Phase 1: Core Framework (30 min) - CRITICAL**
1. **`docs/processes/strategic_collaboration_guide.md`** - How we work together
2. **`CLAUDE.md`** - Project coding standards and workflow  
3. **`docs/DESIGN_PHILOSOPHY.md`** - DR methodology principles

#### **Phase 2: Project Context (45 min) - ESSENTIAL** 
4. **`docs/reports/2025-08-25_dr_plotter_architectural_audit/dr_plotter_audit_strategic_report.md`** - Strategic overview
5. **`docs/audits/d5742c74_cross_category_integration_synthesis.md`** - 8-week roadmap
6. **`docs/plans/02_phase2_design_decisions.md`** - 6 major decisions status

#### **Phase 3: Major Achievements (30 min) - IMPORTANT**
7. **`docs/plans/02_phase2_task_group1_implementation.md`** - Capability architecture
8. **`docs/plans/post_unreserving_migration_report.md`** - 95.8% bypass elimination  
9. **`docs/plans/heatmap_cell_text_implementation_report.md`** - 100% bypass achievement
10. **`docs/api_type_coverage_implementation.md`** - Complete API typing

#### **Phase 4: Current Focus (45 min) - REQUIRED**
11. **`docs/pattern_unification_analysis_report.md`** - **27-page critical analysis**
12. **`docs/figuremanager_decomposition_implementation.md`** - Configuration pattern success
13. **`docs/styleapplicator_method_decomposition_implementation.md`** - Method decomposition approach
14. **`docs/task_group_4_current_status.md`** - **Current exact status and achievements**

---

## **Current Status Summary**

### **Where We Are: Task Group 4 (Pattern Unification)**
- **Phase 1-3 Complete**: Foundation, capability architecture, bypass elimination, API typing
- **Task Group 4**: Final phase - configuration objects + function decomposition
- **Major Achievement**: FigureManager + StyleApplicator decomposition **COMPLETE**

### **What We've Just Accomplished**

#### **✅ FigureManager Decomposition (Complete)**
- **Problem**: 34-parameter constructor explosion
- **Solution**: Configuration objects (`SubplotLayoutConfig`, `FigureCoordinationConfig`, `SubplotFacetingConfig`)
- **Result**: Clean builder pattern, future multi-dimensional subplot support
- **Files**: `src/dr_plotter/figure.py`, `src/dr_plotter/figure_config.py`

#### **✅ StyleApplicator Method Decomposition (Complete)** 
- **Problem**: 67-line, 12-branch critical complexity function
- **Solution**: 7 focused methods within StyleApplicator (intuitive lookup preserved)
- **Result**: 67 lines → 12-line coordinator + focused methods
- **File**: `src/dr_plotter/style_applicator.py`

### **Collaboration Style (Critical to Understand)**

**Evidence-Based Partnership**:
- **Simple questions** → Direct answers
- **Complex problems** → Analysis → Options → Recommendation  
- **All technical claims** must have file:line references
- **Match response complexity** to question complexity

**Quality Standards**:
- **Zero comments policy** - code must be self-documenting
- **Comprehensive typing** - every parameter and return value
- **Fail-fast principles** - assertions over exceptions
- **Systematic patterns** - consistency over individual optimization

**Working Dynamic**:
- Use **TodoWrite** for complex tasks (3+ steps)
- **Evidence over intuition** - validate all claims through investigation
- **Architecture over convenience** - maintain clean boundaries
- **Enhancement over hacks** - systematic solutions improving whole system

### **Next Steps Context**

**Immediate Question**: What remaining Task Group 4 work needs completion?
- Verify StyleApplicator decomposition completeness
- Assess if additional complex functions need decomposition  
- Complete pattern unification across remaining components

**Future Vision**: Enable sophisticated multi-dimensional plotting:
```python
# User's goal - now architecturally ready
faceting = SubplotFacetingConfig(
    facet_by="model_size",      # subplots by model size
    group_by="dataset_name",    # lines by dataset  
    x_col="num_steps", y_col="metric_1"
)
```

### **Success Pattern Recognition**

**What Works**:
- **Systematic investigation** before implementation (evidence-based decisions)
- **Configuration-first approach** (GroupingConfig template pattern)
- **Method decomposition within existing classes** (intuitive lookup)
- **Backward compatibility preservation** (zero breaking changes)
- **Pattern establishment then systematic application**

**Strategic Insight**: We don't just solve individual problems - we **design systematic approaches** that handle entire classes of problems with architectural consistency.

---

## **Ready for Collaboration**

A new agent reading these files will understand:
1. **Project scope and methodology** - systematic architectural enhancement
2. **Current status** - final phase of major transformation
3. **Collaboration patterns** - evidence-based strategic partnership
4. **Quality standards** - DR methodology with zero tolerance for legacy patterns
5. **Recent achievements** - major complexity reduction and pattern establishment
6. **Next steps context** - complete remaining pattern unification

**The systematic approach has been highly successful** - we've achieved massive architectural improvements while maintaining research library flexibility and zero breaking changes.

Welcome to the team! The foundation is solid and we're in the final phase of a highly successful systematic enhancement project. 🚀