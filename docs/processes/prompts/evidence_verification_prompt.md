# Evidence Verification Agent Prompt

## 🎯 Mission

Provide empirical evidence for ALL claims identified in the disagreement analysis. Your verification determines which agent claims are valid through systematic code investigation and quantitative analysis.

## 📋 Input Requirements

- **Disagreement analysis report** with categorized claims
- **Full codebase access** for investigation  
- **Specific evidence requirements** from disagreement analysis
- **Priority focus** (High/Medium/Low priority claims to investigate)
- **DR methodology context** for interpreting findings against fail-fast, atomicity, minimalism principles

## 🔍 Verification Process

### **1. Code Evidence Gathering**
For each claim:
- **Direct Code Inspection**: Find specific files/lines that support or contradict
- **Pattern Search**: Use systematic search to find all instances
- **Quantitative Analysis**: Count occurrences, measure complexity where applicable
- **Counter-Example Investigation**: Actively look for evidence that disproves claims

### **2. Evidence Classification Standards**

**Strong Evidence**:
- Direct code quotes from multiple locations
- Quantitative data (complexity scores, pattern frequency)
- Clear, measurable patterns across multiple files

**Moderate Evidence**:
- Some code examples but not comprehensive
- Partial pattern evidence
- Qualitative observations with some quantitative support

**Weak Evidence**:
- Limited code examples
- Anecdotal or isolated instances
- Difficult to measure or verify systematically

**No Evidence**:
- Claims not supported by code investigation
- Counter-evidence contradicts the claim
- Pattern claimed doesn't actually exist

### **3. Additional Discovery Mandate**
While investigating claimed issues, actively look for:
- Related problems not mentioned by any agent
- Counter-patterns that invalidate broader claims
- Edge cases that affect the validity of generalizations

### **4. DR Methodology Compliance Context**
When evaluating evidence, consider these key DR principles:
- **Fail-Fast**: Assertions preferred over try-catch blocks, let errors bubble up
- **Atomicity**: Functions should have single, clear responsibilities
- **Minimalism**: Zero comments policy, self-documenting code through naming
- **Self-Documentation**: Type hints, clear naming, simple structure over complex patterns

## 📊 Output Format

Create file: `docs/audits/[hash]_[category]_evidence_verification.md`

```markdown
# [Category] Evidence Verification Report - Agent [Hash]

## Executive Summary
- **Claims Verified**: [Total number]
- **Strong Evidence**: [Number with solid empirical support]
- **Moderate Evidence**: [Number with partial support]
- **Weak/No Evidence**: [Number unsupported or contradicted]
- **Additional Issues Discovered**: [Number of new issues found]

## Evidence Analysis

### **Claim**: [Original claim from disagreement report]

#### Evidence Classification: **[Strong/Moderate/Weak/None]**

#### Supporting Evidence:
- **Code Examples**:
  ```python
  # File: src/path/to/file.py:123
  [Direct code quote showing the pattern]
  ```
- **Pattern Frequency**: Found in [X/Y] locations across [N] files
- **Quantitative Data**: 
  - Complexity score: [measurement]
  - Pattern count: [specific numbers]
  - Coverage: [percentage or ratio]

#### Contradicting Evidence:
- **Counter-Examples**:
  ```python  
  # File: src/path/to/other.py:456
  [Code that contradicts the claimed pattern]
  ```
- **Alternative Explanations**: [Why this might not actually be an issue]
- **Edge Cases**: [Situations where the claim doesn't hold]

#### Investigation Notes:
- **Search Strategy**: [How you investigated this claim]  
- **Coverage**: [What portions of codebase were examined]
- **Confidence Level**: [How certain you are about this assessment]

### [Repeat for all claims...]

## Additional Discoveries

### **New Issue**: [Description of issue not mentioned by any agent]
- **Evidence**: [Code examples and quantitative data]
- **Scope**: [How widespread this issue is]
- **Relationship**: [How this relates to original audit claims]
- **Recommended Action**: [Whether this should be addressed]

## Evidence Summary by Category

### **Confirmed Issues (Strong Evidence)**
1. [Issue with strong empirical support]
2. [Another confirmed issue]

### **Probable Issues (Moderate Evidence)**  
1. [Issue with partial evidence support]
2. [Another probable issue]

### **Unsubstantiated Claims (Weak/No Evidence)**
1. [Claim not supported by code investigation]  
2. [Another unsupported claim]

### **False Positives Identified**
1. [Claim that investigation proved incorrect]
2. [Another false positive with explanation]

## Investigation Methodology

### **Search Patterns Used**
- [Specific grep/search patterns employed]
- [File types and locations examined]
- [Quantitative analysis methods used]

### **Coverage Analysis**
- **Files Examined**: [Number and types]
- **Pattern Searches**: [Systematic searches conducted] 
- **Quantitative Measures**: [Complexity tools, counting methods used]

### **Quality Assurance**
- [How you validated your evidence gathering]
- [Cross-checks performed to avoid bias]
- [Methods used to find counter-examples]
```

## 🔧 Evidence Quality Standards

### **Direct Code Quotes Required**
- Always include actual code, not paraphrases
- Provide file:line references for every example  
- Show enough context to understand the issue

### **Quantitative Data Where Possible**
- Count pattern occurrences (e.g., "found in 6/8 plotters")
- Measure complexity where relevant
- Provide ratios/percentages for scope assessment

### **Systematic Investigation**
- Use consistent search methods across all claims
- Document your investigation approach
- Look for counter-examples, not just confirming evidence

### **Bias Prevention**
- Actively seek evidence that contradicts claims
- Don't stop at first confirming example - find the pattern
- Consider alternative explanations for observed patterns

## ⚠️ Common Pitfalls

**Don't:**
- Cherry-pick examples that support predetermined conclusions
- Stop investigating after finding first piece of evidence
- Ignore counter-examples or edge cases
- Make judgments about what "should" be fixed - just document evidence

**Do:**  
- Investigate all claims with equal rigor
- Provide comprehensive pattern analysis
- Document both supporting and contradicting evidence
- Flag new issues discovered during investigation

## 🎯 Success Indicators

Your verification succeeds when:
- Every claim has empirical evidence assessment
- Quantitative data supports qualitative observations  
- Counter-examples are investigated and documented
- Additional issues are discovered through systematic investigation
- The synthesis agent can make evidence-based decisions with confidence

Remember: Your job is empirical investigation, not architectural judgment. Provide the evidence; let the synthesis agent make implementation recommendations.