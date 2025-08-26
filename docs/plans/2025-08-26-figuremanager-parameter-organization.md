# FigureManager Parameter Organization & Theme Integration

## Overview
Systematic reorganization of FigureManager parameter architecture to resolve parameter chaos, fix theme integration conflicts, and establish clean foundation for advanced features like faceted plotting.

**Root Problem**: FigureManager has grown organically with unorganized parameters causing theme conflicts, broken controls, and poor developer experience.

## Evidence Base

### Issues Discovered in Faceted Plotting Project
- **Parameter Chaos**: `plot_margin_bottom`, `legend_y_offset`, `layout_pad`, `legend_ncol`, `legend_strategy` lack logical grouping
- **Theme Conflicts**: Theme system cannot properly integrate due to overlapping parameter responsibilities  
- **Broken Controls**: Visual evidence that margin parameters don't work as expected
- **Poor Developer UX**: 15+ separate parameters with unclear relationships and priorities

### Strategic Impact
- **Blocks Advanced Features**: Can't build robust faceting on unstable foundation
- **Limits Theme System**: Conflicts prevent full themification of layouts
- **Technical Debt**: Parameter proliferation makes maintenance and testing difficult

## Systematic Process

### Phase 1: Current State Analysis
**Objective**: Complete audit of FigureManager parameter architecture and theme system conflicts

**Deliverables**:
- Comprehensive parameter inventory and categorization
- Theme-FigureManager conflict analysis with specific examples
- Identification of broken/non-functional parameters
- Current parameter dependency mapping

**Success Criteria**:
- Complete catalog of all FigureManager parameters
- Clear documentation of theme integration failure points
- Evidence-based priority ranking of parameter issues

### Phase 2: Design Clean Architecture
**Objective**: Design logical parameter organization and theme integration architecture

**Design Decisions**:
- Parameter grouping strategy (layout vs legend vs styling)
- Theme system boundaries and responsibilities  
- Backwards compatibility approach
- Migration path for existing code

**Deliverables**:
- New FigureManager parameter architecture design
- Theme integration specification
- Backwards compatibility strategy
- Implementation roadmap with risk assessment

**Success Criteria**:
- Logical parameter grouping that eliminates conflicts
- Clear theme vs manager responsibility boundaries
- Minimal breaking changes for existing users

### Phase 3: Implementation & Migration
**Objective**: Implement new architecture with systematic migration approach

**Implementation Strategy**:
- Maintain backwards compatibility during transition
- Deprecate old parameters with clear warnings
- Add new organized parameter interfaces
- Fix broken functionality during refactoring

**Deliverables**:
- New parameter architecture implemented
- Theme integration working correctly
- All layout controls functional and tested
- Migration guide and deprecation warnings

**Success Criteria**:
- All existing examples work without modification
- Theme system integrates cleanly with layout controls
- Layout parameters work correctly (margin controls fixed)
- Clear migration path for future parameter additions

### Phase 4: Validation & Documentation
**Objective**: Validate improvements and create comprehensive documentation

**Validation Approach**:
- Test all faceted plotting examples work better with new architecture
- Verify theme system integration eliminates previous conflicts
- Benchmark parameter usability improvements

**Deliverables**:
- Complete parameter reference documentation
- Theme integration examples and best practices
- Performance and usability validation
- Foundation ready for advanced features (faceting)

**Success Criteria**:
- Demonstrable improvement in developer experience
- All theme-manager conflicts resolved
- Clean foundation established for faceted plotting Phase 3b

## Key Architectural Questions

1. **Parameter Grouping Strategy**: How should parameters be logically organized? (LayoutConfig, LegendConfig, etc.)
2. **Theme Integration Boundary**: What parameters belong to themes vs FigureManager?
3. **Backwards Compatibility**: How to minimize breaking changes while fixing architecture?
4. **Migration Strategy**: How to transition existing codebase without disruption?

## Success Metrics

**Immediate**: Organized parameter architecture with working layout controls
**Strategic**: Clean theme integration enabling full styling consistency
**Long-term**: Solid foundation for advanced features like faceted plotting

## Risk Mitigation

**Breaking Changes Risk**: Maintain backwards compatibility with deprecation warnings
**Theme System Risk**: Careful boundary definition to prevent future conflicts  
**Testing Risk**: Comprehensive validation across all existing examples and use cases