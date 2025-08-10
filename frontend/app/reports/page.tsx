'use client'

import { useState, useRef } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  FileText,
  Search,
  Download,
  Calendar,
  Filter,
  TrendingUp,
  Eye,
  X
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface Report {
  id: string
  title: string
  type: 'daily' | 'weekly' | 'monthly'
  date: string
  status: 'delivered' | 'processing' | 'draft'
  articleCount: number
  highPriority: number
  avgRelevance: number
  content?: string
}

const mockReports: Report[] = [
  {
    id: '1',
    title: 'Daily AI Intelligence Brief',
    type: 'daily',
    date: new Date().toISOString(),
    status: 'delivered',
    articleCount: 24,
    highPriority: 3,
    avgRelevance: 87,
    content: `
# Daily AI Intelligence Brief - ${formatDate(new Date())}

## Executive Summary
Today's analysis reveals significant developments in AI research and industry applications. Our intelligence system processed 24 articles from tier-1 sources with an average relevance score of 87%, indicating exceptional content quality. Three high-priority developments require immediate attention, while broader trends show accelerating enterprise adoption and increasing regulatory focus.

## 🚨 High Priority Intelligence Items

### 1. OpenAI Announces GPT-4.5 with Enhanced Reasoning Capabilities
**Strategic Impact**: Critical advancement in large language model capabilities
**Details**: OpenAI today unveiled GPT-4.5, representing a 40% performance improvement in reasoning tasks compared to GPT-4. The model demonstrates exceptional capabilities in mathematical problem-solving, code generation, and complex logical reasoning. Key improvements include extended context length (200K tokens), enhanced factual accuracy, and reduced hallucination rates. Enterprise customers report significant productivity gains in software development and data analysis workflows.

**Business Implications**: Organizations currently using GPT-4 should evaluate upgrade pathways. The enhanced reasoning capabilities particularly benefit financial modeling, legal document analysis, and scientific research applications. Expect competitive pressure on Google, Anthropic, and other AI model providers.

### 2. Google Accelerates Gemini Pro Enterprise Rollout Across Fortune 500
**Strategic Impact**: Major shift in enterprise AI adoption patterns
**Details**: Google announced that Gemini Pro is now available to all Fortune 500 companies through Google Cloud Platform, with specialized deployment support and enterprise-grade security features. The rollout includes industry-specific fine-tuning for healthcare, finance, and manufacturing sectors. Early adopters report 35% efficiency gains in document processing and customer service automation.

**Business Implications**: This represents Google's most aggressive push into enterprise AI markets. Organizations using Microsoft's Azure OpenAI Service should reassess vendor strategies. The move signals intensifying competition in the enterprise AI space, potentially leading to price pressure and enhanced features.

### 3. Congressional AI Regulation Bill Advances Through Committee
**Strategic Impact**: Regulatory framework taking shape with compliance implications
**Details**: The House Energy and Commerce Committee approved bipartisan legislation requiring algorithmic transparency for AI systems processing over 10 million user interactions annually. The bill mandates public disclosure of training methodologies, bias testing results, and safety evaluation protocols. Implementation timeline suggests requirements will be active within 18 months.

**Business Implications**: Organizations deploying AI systems at scale should begin compliance preparation immediately. Required documentation includes model training data sources, bias mitigation strategies, and ongoing monitoring protocols. Expect similar legislation in EU and other jurisdictions.

## 📊 Intelligence Analysis Metrics

### Content Quality Assessment
- **Total Articles Processed**: 24 (100% successfully analyzed)
- **Average Relevance Score**: 87% (significantly above 75% threshold)
- **Source Reliability**: All sources maintain Tier 1-2 credibility ratings
- **Processing Efficiency**: $0.089 total cost, maintaining $0.0037 per article target

### Content Distribution by Category
- **Research & Development**: 8 articles (33%) - Focus on multimodal AI and reasoning improvements  
- **Enterprise Solutions**: 5 articles (21%) - B2B AI tool launches and case studies
- **Policy & Governance**: 4 articles (17%) - Regulatory developments and ethical AI discussions
- **Investment & Funding**: 7 articles (29%) - VC funding, IPO preparations, and M&A activity

## 🏢 Strategic Industry Intelligence

### Emerging Technology Patterns
**Multimodal AI Systems**: Analysis indicates 67% increase in coverage of vision-language models compared to previous week. Key developments include improved image understanding, video analysis capabilities, and cross-modal reasoning. Major players (OpenAI, Google, Microsoft) are prioritizing multimodal capabilities for enterprise applications.

**AI Safety & Alignment**: Growing emphasis on responsible AI development, with 43% of research articles addressing safety considerations. Notable focus areas include constitutional AI methods, interpretability research, and human feedback integration. Regulatory pressure is driving increased investment in safety research.

**Enterprise Deployment Acceleration**: Business adoption patterns show 78% of featured case studies involve production deployments rather than pilot programs. Key success factors include executive sponsorship, dedicated AI teams, and phased implementation strategies.

### Competitive Intelligence Highlights
- **OpenAI**: Expanding enterprise focus with enhanced API capabilities and industry partnerships
- **Google**: Aggressive enterprise push through cloud platform integration and vertical-specific solutions  
- **Microsoft**: Strengthening position through Office 365 integration and Azure AI services
- **Anthropic**: Focusing on safety-first approach for enterprise customers requiring high-reliability AI

## 📈 Market Trend Analysis

### Weekly Trend Indicators
1. **Enterprise AI Budgets**: 23% increase in reported AI spending allocations for Q4 2025
2. **Developer Adoption**: Code generation tools showing 156% month-over-month growth
3. **Regulatory Preparation**: 89% of large tech companies establishing AI governance committees
4. **Open Source Momentum**: Community-driven models gaining enterprise validation

### Risk Assessment
- **Regulatory Compliance**: Increasing complexity requires dedicated legal and technical resources
- **Model Dependency**: Over-reliance on single AI providers creates strategic vulnerabilities  
- **Talent Competition**: AI expertise shortage intensifying across all sectors
- **Security Considerations**: AI systems becoming attractive targets for adversarial attacks

## 🎯 Source Performance Intelligence

### Tier 1 Source Analysis
1. **TechCrunch** (6 articles, 92% relevance): Exceptional coverage of funding rounds and product launches
2. **MIT Technology Review** (3 articles, 94% relevance): Deep technical analysis with strong research connections
3. **Ars Technica** (4 articles, 89% relevance): Balanced technical and business perspective
4. **The Verge** (5 articles, 84% relevance): Consumer-focused AI applications and market trends
5. **Wired** (6 articles, 86% relevance): Long-form analysis of AI societal implications

### Source Reliability Metrics
- **Fact-checking accuracy**: 97.3% across all sources
- **Source diversity**: 13 active feeds ensuring comprehensive coverage
- **Update frequency**: Average 3.2 articles per source daily
- **Editorial quality**: 91% of articles meet professional journalism standards

## 💰 Cost Optimization & Efficiency

### Processing Economics
- **Cost per Article**: $0.0037 (maintaining target efficiency)
- **Monthly Projection**: $2.67 (89% under allocated budget)
- **Quality-Cost Ratio**: 23.5 relevance points per cent (industry-leading efficiency)
- **Processing Speed**: Average 2.3 seconds per article analysis

### Resource Allocation
- **AI Model Usage**: 67% GPT-4o-mini, 33% premium models for complex analysis
- **Storage Costs**: Vector embeddings and full-text indexing optimized for sub-second search
- **API Efficiency**: Batch processing reducing per-request overhead by 34%

## 🔮 Strategic Recommendations

### Immediate Actions (Next 24 Hours)
1. **Monitor GPT-4.5 availability** for potential competitive advantages
2. **Assess Gemini Pro enterprise features** for cost-benefit analysis
3. **Review AI compliance frameworks** in preparation for regulatory requirements

### Short-term Priorities (Next 7 Days)
1. **Evaluate multimodal AI applications** for business process enhancement
2. **Strengthen AI governance procedures** ahead of regulatory implementation
3. **Assess vendor diversification strategies** to reduce single-provider dependencies

---
**Intelligence Report Generated**: ${new Date().toLocaleString()}  
**Next Scheduled Analysis**: ${formatDate(new Date(Date.now() + 24 * 60 * 60 * 1000))} at 6:00 AM  
**Coverage**: 13 Premium Sources • 152+ Articles in Database • 24/7 Monitoring Active
    `
  },
  {
    id: '2',
    title: 'Weekly Trend Analysis',
    type: 'weekly',
    date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'processing',
    articleCount: 156,
    highPriority: 12,
    avgRelevance: 84
  },
  {
    id: '3',
    title: 'Monthly Intelligence Report',
    type: 'monthly',
    date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    status: 'delivered',
    articleCount: 623,
    highPriority: 47,
    avgRelevance: 86,
    content: `
# Monthly AI Intelligence Report - ${formatDate(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))}

## Executive Summary
This comprehensive monthly analysis covers 623 articles processed over the past 30 days,
revealing significant trends and developments in the AI landscape.

## Key Insights

### 📊 Processing Metrics
- **Total Articles**: 623 articles from 13 premium sources
- **High Priority Events**: 47 critical developments identified
- **Average Quality**: 86% relevance score maintained
- **Total Processing Cost**: $2.31 ($0.0037 per article)

### 🎯 Major Themes
1. **Large Language Models Evolution** - 23% of coverage
2. **Enterprise AI Adoption** - 19% of coverage
3. **AI Safety & Alignment** - 16% of coverage
4. **Multimodal AI Systems** - 15% of coverage
5. **AI Regulation & Policy** - 13% of coverage
6. **Open Source AI Development** - 14% of coverage

### 🏆 Top Performing Sources
1. **MIT Technology Review** - 94% avg relevance (42 articles)
2. **TechCrunch** - 92% avg relevance (128 articles)
3. **Ars Technica** - 89% avg relevance (87 articles)
4. **Nature AI** - 96% avg relevance (23 articles)
5. **OpenAI Blog** - 95% avg relevance (18 articles)

### 📈 Industry Analysis
- **Research Publications**: 234 articles (37.5%)
- **Product Announcements**: 156 articles (25.0%)
- **Funding & Investment**: 98 articles (15.7%)
- **Policy & Regulation**: 78 articles (12.5%)
- **Technical Analysis**: 57 articles (9.1%)

## Cost Optimization Results
- **Target**: $5.00/month | **Actual**: $2.31/month
- **Efficiency Gain**: 54% under budget
- **Cost per Quality Article**: $0.0037
- **Projected Annual Cost**: $27.72

---
Report Generated: ${new Date().toLocaleString()}
Intelligence Coverage: 13 Premium Sources
Next Report: ${formatDate(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000))}
    `
  }
]

async function generatePDF(report: Report) {
  // Simple PDF generation using browser print
  const printWindow = window.open('', '_blank')
  if (!printWindow) return

  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${report.title}</title>
      <style>
        body { 
          font-family: system-ui, -apple-system, sans-serif; 
          margin: 40px; 
          line-height: 1.6; 
          color: #333;
        }
        h1 { color: #1e40af; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
        h2 { color: #1f2937; margin-top: 30px; }
        h3 { color: #374151; }
        .metrics { background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .priority { background: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 10px 0; }
        @media print { body { margin: 20px; } }
      </style>
    </head>
    <body>
      ${report.content?.replace(/\n/g, '<br>').replace(/###/g, '<h3>').replace(/##/g, '<h2>').replace(/#/g, '<h1>') || 'Report content not available'}
    </body>
    </html>
  `

  printWindow.document.write(htmlContent)
  printWindow.document.close()
  
  setTimeout(() => {
    printWindow.print()
  }, 500)
}

export default function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false)

  const handleViewReport = (report: Report) => {
    setSelectedReport(report)
  }

  const handleDownloadPDF = async (report: Report) => {
    if (!report.content) {
      alert('Report content not available for download')
      return
    }

    setIsGeneratingPDF(true)
    try {
      await generatePDF(report)
    } catch (error) {
      console.error('PDF generation failed:', error)
      alert('PDF generation failed. Please try again.')
    } finally {
      setIsGeneratingPDF(false)
    }
  }

  const filteredReports = mockReports.filter(report => 
    report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    report.type.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (selectedReport) {
    return (
      <div className="space-y-6">
        {/* Report Viewer Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{selectedReport.title}</h1>
            <p className="text-muted-foreground">
              {formatDate(new Date(selectedReport.date))} • {selectedReport.articleCount} articles analyzed
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              onClick={() => handleDownloadPDF(selectedReport)}
              disabled={isGeneratingPDF || !selectedReport.content}
              variant="default"
            >
              <Download className="h-4 w-4 mr-2" />
              {isGeneratingPDF ? 'Generating PDF...' : 'Download PDF'}
            </Button>
            <Button
              onClick={() => setSelectedReport(null)}
              variant="outline"
            >
              <X className="h-4 w-4 mr-2" />
              Close
            </Button>
          </div>
        </div>

        {/* Report Content */}
        <Card>
          <CardContent className="pt-6">
            {selectedReport.content ? (
              <div className="prose prose-sm max-w-none">
                <div 
                  dangerouslySetInnerHTML={{ 
                    __html: selectedReport.content
                      .replace(/\n/g, '<br>')
                      .replace(/###\s+(.+)/g, '<h3>$1</h3>')
                      .replace(/##\s+(.+)/g, '<h2>$1</h2>')
                      .replace(/#\s+(.+)/g, '<h1>$1</h1>')
                      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*(.+?)\*/g, '<em>$1</em>')
                  }} 
                />
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Report content is being generated...</p>
                <p className="text-sm mt-2">This report will be available once processing is complete.</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground">
          AI-generated intelligence reports and analysis summaries
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search reports..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button variant="outline" className="sm:w-auto">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
        <Button variant="outline" className="sm:w-auto">
          <Calendar className="h-4 w-4 mr-2" />
          Date Range
        </Button>
      </div>

      {/* Reports Grid */}
      <div className="grid gap-6">
        {filteredReports.map((report) => (
          <Card key={report.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <Link 
                      href={`/reports/${report.id}/articles`}
                      className="hover:text-blue-600 transition-colors cursor-pointer"
                    >
                      {report.title}
                    </Link>
                  </CardTitle>
                  <CardDescription>
                    {formatDate(new Date(report.date))} • 
                    <Link 
                      href={`/reports/${report.id}/articles`}
                      className="hover:text-blue-600 transition-colors ml-1"
                    >
                      {report.articleCount} articles analyzed
                    </Link>
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Badge 
                    variant={report.status === 'delivered' ? 'default' : 'secondary'}
                    className={
                      report.status === 'delivered' 
                        ? 'bg-green-100 text-green-800'
                        : report.status === 'processing' 
                        ? 'bg-yellow-100 text-yellow-800' 
                        : 'bg-gray-100 text-gray-800'
                    }
                  >
                    {report.status}
                  </Badge>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleViewReport(report)}
                    disabled={!report.content}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleDownloadPDF(report)}
                    disabled={!report.content || isGeneratingPDF}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    {isGeneratingPDF ? 'Generating...' : 'PDF'}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{report.articleCount}</div>
                    <div className="text-sm text-blue-600">Articles Analyzed</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{report.highPriority}</div>
                    <div className="text-sm text-green-600">High Priority Items</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{report.avgRelevance}%</div>
                    <div className="text-sm text-purple-600">Avg Relevance Score</div>
                  </div>
                </div>
                {report.status === 'processing' && (
                  <div className="text-sm text-muted-foreground">
                    {report.type.charAt(0).toUpperCase() + report.type.slice(1)} analysis in progress. 
                    Report will be available in approximately 15 minutes.
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}