# Plotter Kwargs Routing - Full Impact Analysis

## Context

We want to implement systematic `plotter_kwargs` routing through the figure manager that flows through the theme system as overrides. This will enable users to pass plotter-specific configuration systematically rather than having "stranded parameters" in plotter code.

The key architectural decision: **Remove all backward compatibility constraints** to achieve the cleanest possible design.

## Task

Analyze the complete scope of changes required to implement this system without backward compatibility. Identify everything that would need to change, break, or be redesigned.

## Analysis Requirements

### 1. Current Parameter Flow Mapping
- Map every current pathway for plotter-specific parameters to reach plotters
- Document all current override mechanisms and precedence rules
- Identify all places where theme parameters are applied vs. kwargs parameters
- Find all "stranded parameters" that exist in plotter code but lack API routes

### 2. Theme System Integration Points
- How would `plotter_kwargs` integrate with the existing StyleApplicator precedence system?
- Where in the theme hierarchy would plotter-specific overrides sit?
- What changes to theme inheritance and resolution logic would be needed?
- How would this interact with existing plot_styles, axes_styles, etc.?

### 3. Figure Manager Changes
- What new parameters would FigureManager need to accept?
- How would `plotter_kwargs` be stored and passed through to individual plot calls?
- What validation would be needed for plotter-specific parameters?
- How would this interact with the existing figure/legend/theme configuration objects?

### 4. Plotter Architecture Changes
- How would individual plotters receive and process the new parameter routing?
- What changes to plotter constructors would be needed?
- How would this interact with existing component schemas?
- Would plotters need new initialization patterns?

### 5. User API Breaking Changes
- What current user code would break with this new system?
- What parameters would be deprecated/removed from current APIs?
- What new user patterns would replace current approaches?
- How would existing theme-based parameter setting change?

### 6. Component Schema Impact
- How would component schemas need to change to support systematic routing?
- What new schema patterns would be needed?
- Would the schema validation system need updates?
- How would this affect the existing phase-based styling system?

### 7. Testing and Validation Changes
- What test patterns would break and need updating?
- What new test coverage would be needed for parameter routing?
- How would theme override testing need to change?
- What validation logic would need to be added/updated?

### 8. Documentation and Examples Impact
- Which example files would need complete rewrites?
- What documentation patterns would become obsolete?
- What new user guidance would be needed?
- How would the theme system documentation change?

## Deliverable

Provide a comprehensive analysis covering:

1. **Architectural Changes**: Every system component that would need modification
2. **Breaking Changes**: Complete list of user-facing API changes with before/after examples
3. **Implementation Scope**: Estimated complexity and interdependencies 
4. **Migration Path**: What would need to change in user code
5. **Risk Assessment**: What could go wrong with this level of change
6. **Validation Strategy**: How to ensure the new system works correctly

## Success Criteria

The analysis should be detailed enough that we can:
- Make an informed decision about whether to proceed
- Understand the full scope before starting implementation
- Plan the implementation sequence to minimize breakage
- Anticipate user migration challenges

Focus on being comprehensive rather than making recommendations - we want to understand the full impact first.