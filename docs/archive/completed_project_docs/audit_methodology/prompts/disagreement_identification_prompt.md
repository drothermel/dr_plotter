# Disagreement Identification Agent Prompt

## 🎯 Mission

Systematically analyze multiple audit reports for a single category to identify areas of consensus vs conflict. Your analysis enables evidence-based resolution of agent disagreements.

## 📋 Input Requirements

- **3-5 audit reports** for the same category (e.g., all "architectural consistency" reports)
- **Same category focus**: All reports must address the same architectural area
- **Agent diversity**: Reports should come from different agents/perspectives
- **DR Plotter context**: Reports analyze dr_plotter codebase following DR methodology principles

## 🔍 Analysis Process

### **1. Consensus Analysis**
Identify claims where **≥75% of agents agree**:
- Look for similar issues mentioned across multiple reports
- Note consistent recommendations across agents
- Identify patterns that multiple agents discovered independently

### **2. Conflict Detection**
Identify **specific disagreements** between agents:
- Agent A says X is a problem, Agent B says X is working well
- Different assessments of severity (critical vs minor)
- Contradictory recommendations for same issue

### **3. Novel Claim Identification**
Flag issues **mentioned by only one agent**:
- Unique discoveries that others missed
- Agent-specific perspectives or expertise areas
- Potential blind spots in other agents' analysis

### **4. Evidence Requirements**
For each claim type, specify what evidence would resolve uncertainty:
- File/line references needed
- Quantitative data required
- Specific patterns to investigate

## 📊 Output Format

Create file: `docs/audits/[hash]_[category]_disagreement_analysis.md`

```markdown
# [Category] Disagreement Analysis - Agent [Hash]

## Executive Summary
- **Total Reports Analyzed**: [Number]
- **Consensus Claims**: [Number where ≥75% agree]
- **Disputed Claims**: [Number with clear disagreement]
- **Novel Claims**: [Number mentioned by single agent]
- **Evidence Resolution Required**: [Number of claims needing verification]

## Consensus Claims (≥75% Agent Agreement)

### **Claim**: [Issue description]
- **Agent Agreement**: [X/Y agents identified this]
- **Consistency Level**: [Identical/Similar/Related descriptions]
- **Evidence Needed**: [Specific verification to confirm]
- **Priority Indication**: [Most agents rated this as Critical/High/Medium/Low]

## Disputed Claims (Agent Disagreement)

### **Claim**: [Issue description]
- **Agent Positions**:
  - Agent [ID]: [Position/assessment]
  - Agent [ID]: [Different position/assessment]
- **Disagreement Type**: [Assessment/Severity/Recommendation/Existence]
- **Evidence Needed**: [What would resolve this disagreement]
- **Resolution Path**: [How verification could determine truth]

## Novel Claims (Single Agent)

### **Claim**: [Issue description]  
- **Source Agent**: [Agent identifier]
- **Uniqueness Factor**: [Why other agents might have missed this]
- **Evidence Needed**: [Verification to determine validity]
- **Potential Impact**: [If true, what would this mean]

## Evidence Requirements Summary

### **High Priority Verification**
- [Claims that need immediate empirical validation]

### **Medium Priority Verification**  
- [Claims where evidence would be valuable but less critical]

### **Pattern Analysis Required**
- [Claims requiring codebase-wide pattern investigation]

### **Quantitative Analysis Required**
- [Claims needing complexity scores, frequency counts, metrics]
```

## 🔧 Quality Standards

### **Thoroughness**
- Every significant claim from every report must be categorized
- Don't ignore minor disagreements - they may indicate important edge cases
- Look for subtle conflicts, not just obvious contradictions

### **Specificity**
- Quote specific agent statements when showing disagreement
- Be precise about what evidence would resolve each uncertainty
- Distinguish between different types of disagreement (existence, severity, solution)

### **Systematic Coverage**
- Organize findings consistently across all reports
- Use same evidence categorization for all claims
- Ensure no agent perspectives are accidentally overlooked

## ⚠️ Common Pitfalls

**Don't:**
- Attempt to resolve disagreements yourself - just identify them
- Dismiss novel claims as less important than consensus
- Group unrelated issues together for convenience
- Make judgments about which agent is "probably right"

**Do:**
- Focus on clear identification and categorization
- Specify exactly what evidence would be needed
- Note when disagreements reveal important edge cases
- Preserve the specific language agents used

## 🎯 Success Indicators

Your analysis succeeds when:
- All significant claims are systematically categorized
- Evidence requirements are specific and actionable
- Disagreements are clearly articulated without bias
- The verification agent can immediately understand what to investigate
- No important agent perspectives are lost or overlooked

Remember: Your job is systematic identification, not resolution. The evidence verification stage will determine which claims are valid.