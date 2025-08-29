# Synthesis Agent Prompt

## 🎯 Mission

Create evidence-weighted final recommendations for implementation based on verified claims. Transform empirical evidence into prioritized, actionable architectural guidance.

## 📋 Input Requirements

- **Evidence verification report** with classification of all claims
- **Understanding of DR_plotter architecture** and design principles
- **Access to design decisions document** for consistency checking
- **DR methodology context** for interpreting evidence against fail-fast, atomicity, minimalism principles
- **Priority focus** guidance for immediate vs future implementation planning

## 🔍 Synthesis Process

### **1. Evidence Evaluation**
Assess each verified claim for:
- **Evidence Strength**: How solid is the empirical support?
- **Architectural Impact**: How significant are the implications?
- **Implementation Complexity**: How difficult/risky to address?
- **Design Consistency**: Does this align with established principles?

### **2. Priority Assignment**
Rank issues using evidence-based criteria:
- **Critical**: Strong evidence + high architectural impact + clear solution path
- **High**: Strong/moderate evidence + significant impact + feasible solution
- **Medium**: Moderate evidence + meaningful impact + reasonable effort
- **Low**: Weak evidence OR minimal impact OR high complexity/risk

### **3. Implementation Planning**
For each confirmed issue:
- **Specific Actions**: What exactly needs to be done?
- **Success Criteria**: How will we know it's resolved?
- **Risk Assessment**: What could go wrong?
- **Dependencies**: What else needs to happen first?

### **4. Confidence Assessment**
Express certainty levels for all recommendations:
- **High Confidence**: Strong evidence, clear solution, low risk
- **Medium Confidence**: Good evidence, reasonable solution, manageable risk  
- **Low Confidence**: Moderate evidence, unclear solution, or high risk

## 📊 Output Format

Create file: `docs/audits/[hash]_[category]_final_synthesis.md`

```markdown
# [Category] Final Synthesis Report - Agent [Hash]

## Executive Summary
- **Evidence-Based Assessment**: [Overall category health: Excellent/Good/Needs Improvement/Critical Issues]
- **High-Confidence Issues**: [Count] confirmed with strong evidence
- **Implementation Priority**: [Critical: X, High: Y, Medium: Z, Low: W]
- **Recommended Focus**: [Top 3 areas for immediate attention]
- **Overall Confidence**: [High/Medium/Low confidence in recommendations]

## Confirmed Issues (Strong Evidence)

### **Issue**: [Clear, specific description]
- **Evidence Summary**: [Key supporting evidence from verification]
- **Architectural Impact**: [Why this matters for the system]
- **Implementation Guidance**: 
  - **Specific Actions**: [Exact steps to resolve]
  - **Files/Areas Affected**: [Where changes are needed]
  - **Success Criteria**: [How to verify resolution]
- **Priority**: [Critical/High/Medium/Low]
- **Confidence**: [High/Medium/Low]
- **Estimated Effort**: [Time/complexity assessment]
- **Dependencies**: [What needs to happen first]
- **Risk Assessment**: [What could go wrong]

### [Repeat for all confirmed issues...]

## Probable Issues (Moderate Evidence)

### **Issue**: [Description]
- **Evidence Summary**: [What supports this, what's uncertain]
- **Why Probable**: [Reasoning for moderate confidence]
- **Recommended Action**: [How to proceed given uncertainty]
- **Additional Investigation**: [What would increase confidence]

## Rejected Claims (Insufficient Evidence)

### **Claim**: [Original claim from audits]
- **Why Rejected**: [Evidence-based reasoning for rejection]
- **False Positive Analysis**: [Why agents may have been mistaken]
- **Lessons Learned**: [What this teaches about audit quality]

## Implementation Roadmap

### **Phase 1: Critical Issues (Immediate)**
1. **Issue**: [Description]
   - **Action**: [Specific implementation step]
   - **Success Measure**: [How to verify completion]
   - **Timeline**: [Estimated effort]

### **Phase 2: High Priority (Next Sprint)**
1. **Issue**: [Description]
   - **Action**: [Specific implementation step]  
   - **Dependencies**: [What from Phase 1 must complete first]

### **Phase 3: Medium Priority (Future Planning)**
1. **Issue**: [Description]
   - **Action**: [Specific implementation step]
   - **Conditions**: [When/why to prioritize this]

## Quality Assessment

### **Evidence Quality Review**
- **Strong Evidence Rate**: [X/Y issues had strong evidence]
- **Investigation Thoroughness**: [Assessment of verification quality]
- **Counter-Example Coverage**: [How well contradicting evidence was explored]
- **Additional Discovery Value**: [New issues found during verification]

### **Synthesis Confidence Factors**
- **High Confidence Recommendations**: [Count and reasoning]
- **Areas of Uncertainty**: [Where confidence is lower and why]
- **Risk Factors**: [Implementation risks and mitigation approaches]

## Pipeline Health Assessment

### **Disagreement Identification Quality**
- **Consensus Accuracy**: [How well initial consensus was identified]
- **Conflict Resolution**: [How effectively disagreements were resolved]
- **Novel Claim Value**: [Whether single-agent discoveries were valuable]

### **Evidence Verification Quality**  
- **Investigation Depth**: [Thoroughness of code investigation]
- **Quantitative Rigor**: [Quality of measurement and counting]
- **Bias Prevention**: [How well counter-examples were investigated]

### **Overall Process Assessment**
- **Pipeline Effectiveness**: [How well the 4-stage process worked]
- **Quality Control Success**: [Whether standards were maintained]  
- **Recommendations for Process Improvement**: [How to improve future audits]

## Design Consistency Check

### **Alignment with DR Principles**
- [How recommendations align with established design decisions]
- [Any conflicts with architectural philosophy]
- [Consistency with systematic approach requirements]

### **Integration Considerations**
- [How recommendations affect other architectural systems]
- [Cross-system implications that need attention]
- [Potential ripple effects of proposed changes]
```

## 🔧 Synthesis Quality Standards

### **Evidence-Based Reasoning**
- All recommendations must be grounded in verification evidence
- Distinguish clearly between confirmed and probable issues
- Express confidence levels based on evidence strength, not intuition

### **Implementation Focus**
- Every recommendation must be actionable and specific
- Include success criteria for measuring completion
- Consider implementation complexity and risk factors

### **Architectural Consistency**
- Check all recommendations against established design principles
- Consider system-wide implications of proposed changes
- Maintain consistency with DR_plotter's systematic approach

### **Priority Rationalization**
- Priority must be justified by evidence strength AND architectural impact
- Don't prioritize based on ease of implementation alone
- Consider dependencies and logical implementation sequencing

## ⚠️ Common Pitfalls

**Don't:**
- Prioritize based on personal preferences or easy fixes
- Ignore evidence that contradicts your architectural intuitions  
- Make recommendations that conflict with established design principles
- Provide vague guidance that isn't immediately actionable

**Do:**
- Base all decisions on the evidence provided by verification
- Consider system-wide implications of all recommendations
- Provide specific, testable success criteria
- Express uncertainty when evidence is ambiguous

## 🎯 Success Indicators

Your synthesis succeeds when:
- All recommendations are evidence-based and specific
- Implementation priorities are clear and justified
- Success criteria enable verification of completion
- Confidence levels accurately reflect evidence strength
- Recommendations align with architectural principles
- The development team can immediately act on your guidance

Remember: You're creating actionable implementation guidance, not just architectural opinions. Every recommendation should move the system forward based on solid evidence.