# LinkedIn Automation Best Practices

## Core Principles

### 1. **Quality Over Quantity**
Don't aim to connect with everyone. Focus on high-value prospects who match your ideal customer profile (ICP).

### 2. **Personalization at Scale**
Use data-driven personalization rather than generic templates. Reference profile data, shared connections, and relevant context.

### 3. **Multi-Touch Strategy**
Don't rely on a single channel or message. Combine LinkedIn, email, Twitter, and content engagement.

### 4. **Patience and Persistence**
Building relationships takes time. Space out touchpoints and provide value at each step.

### 5. **Compliance First**
Always respect platform limits and terms of service. One restricted account can damage your brand.

## LinkedIn Lookback Integration Strategy

### Phase 1: Tracking & Intelligence (Week 1-2)
**Goal:** Build activity database and identify patterns

**Actions:**
1. Install LinkedIn Lookback extension
2. Use LinkedIn normally for 1-2 weeks
3. Track profile views, connections, messages
4. Review activity patterns and engagement

**Metrics:**
- Profile views per day
- Connection acceptance rate
- Message response rate
- Time to response

### Phase 2: Lead Qualification (Week 3-4)
**Goal:** Score and prioritize leads based on engagement signals

**Actions:**
1. Sync Lookback data to 10x-Team
2. Enrich profiles with Exa AI
3. Score leads based on:
   - Multiple profile visits
   - Connection degree
   - Company/title match to ICP
   - Engagement with your content

**Lead Scoring Example:**
```javascript
function calculateLeadScore(profile, activities) {
  let score = 0;

  // Multiple interactions = higher interest
  const viewCount = activities.filter(a =>
    a.activity_type === 'profile_view' &&
    a.linkedin_url === profile.url
  ).length;
  score += Math.min(viewCount * 10, 30); // Cap at 30

  // ICP match
  if (profile.title.match(/Director|VP|C-Level/)) score += 20;
  if (profile.company_size > 50) score += 10;
  if (profile.industry === targetIndustry) score += 15;

  // Connection degree (1st = warm, 2nd = medium, 3rd = cold)
  if (profile.connection_degree === '1st') score += 25;
  else if (profile.connection_degree === '2nd') score += 15;
  else score += 5;

  // Shared connections (social proof)
  score += Math.min(profile.shared_connections * 2, 10);

  return score; // Max score: 100
}

// Prioritize leads
if (score >= 70) priority = 'high';
else if (score >= 50) priority = 'medium';
else priority = 'low';
```

### Phase 3: Automated Outreach (Week 5+)
**Goal:** Execute multi-touch campaigns with personalization

**Actions:**
1. Start with high-priority leads only
2. Implement rate-limited automation
3. Monitor acceptance/response rates
4. Adjust strategy based on data

## Outreach Campaign Templates

### Campaign 1: Profile View → Connection Request
**Timeline:** 24-48 hours after first profile view

**Trigger:**
```javascript
// Auto-trigger if:
// - Profile viewed once
// - Matches ICP criteria
// - Lead score >= 50
// - No existing connection or pending request
```

**Message Template:**
```
Hi {{first_name}},

I came across your profile while researching {{industry}} leaders in {{location}}.

Your experience at {{company}} caught my attention—I've been following their work in {{relevant_area}}.

I'd love to connect and stay in touch.

Best,
{{your_name}}
```

**Variables:**
- `{{first_name}}`: From profile data
- `{{industry}}`: From company data
- `{{location}}`: From profile data
- `{{company}}`: Current company
- `{{relevant_area}}`: Researched via Exa AI

### Campaign 2: Connection Accepted → Introduction
**Timeline:** 48-72 hours after connection accepted

**Trigger:**
```javascript
// Auto-trigger if:
// - Connection request accepted
// - No prior messages sent
// - Lead score >= 60
```

**Message Template:**
```
Thanks for connecting, {{first_name}}!

I noticed you're {{current_title}} at {{company}}. We help companies like yours {{value_proposition}}.

Would it make sense to have a quick chat about {{specific_pain_point}}?

I've seen success with companies like {{similar_company_1}} and {{similar_company_2}}.

Let me know if you're interested—happy to share more.

{{your_name}}
```

**Personalization:**
- `{{value_proposition}}`: Based on company industry
- `{{specific_pain_point}}`: Researched via Exa AI
- `{{similar_company_X}}`: Case studies from same industry

### Campaign 3: No Reply → Email Follow-up
**Timeline:** 5 days after LinkedIn message with no reply

**Trigger:**
```javascript
// Auto-trigger if:
// - LinkedIn message sent 5+ days ago
// - No reply received
// - Email address available
// - Lead score >= 70
```

**Email Template:**
```
Subject: Quick follow-up from LinkedIn

Hi {{first_name}},

I reached out on LinkedIn last week but wanted to follow up via email in case you missed it.

I help {{job_title}}s at {{company_size}} companies {{solve_problem}}.

For example, we recently helped {{case_study_company}} {{specific_result}}.

Would it make sense to have a brief call to explore if we could do something similar for {{company}}?

You can book time directly here: [calendar_link]

Best,
{{your_name}}
{{your_title}}
{{your_company}}
```

**Multi-Touch Sequence:**
- Day 0: LinkedIn connection request
- Day 2: Connection accepted
- Day 4: Intro message
- Day 9: Email follow-up #1
- Day 14: Email follow-up #2 (different angle)
- Day 21: Final email (break-up message)

### Campaign 4: Warm Lead Re-engagement
**Timeline:** For leads who viewed your profile multiple times

**Trigger:**
```javascript
// Auto-trigger if:
// - Profile viewed 3+ times
// - Not yet connected
// - High ICP match
```

**Message Template:**
```
Hi {{first_name}},

I noticed we've been checking out each other's profiles—figured I'd reach out directly!

I'm helping {{industry}} companies {{solve_problem}}. Based on your role at {{company}}, thought this might be relevant.

Open to connecting?

{{your_name}}
```

**Why This Works:**
- Acknowledges mutual interest
- Low-pressure ask
- Shows awareness
- Creates reciprocity

## Enrichment Strategy

### Data to Collect

#### From LinkedIn Lookback
- Profile name, title, company
- Location, education, connection degree
- Activity history (views, connections, messages)
- Engagement patterns

#### From Exa AI Enrichment
- Company funding stage and investors
- Tech stack and tools used
- Recent company news and hiring
- Personal interests and content shared
- GitHub/Twitter/personal website

#### From Additional Sources
- Company website and blog
- G2/Capterra reviews (for B2B)
- LinkedIn company page posts
- Shared connections and introductions
- Recent job changes or promotions

### Enrichment Workflow

```javascript
async function enrichProspect(linkedinUrl) {
  // Step 1: Get base data from Lookback
  const baseData = await getLookbackData(linkedinUrl);

  // Step 2: Enrich with Exa AI
  const exaData = await exaSearch({
    query: `${baseData.profile_name} ${baseData.company}`,
    type: 'neural',
    num_results: 10
  });

  // Step 3: Extract company intelligence
  const companyData = await enrichCompany(baseData.company);

  // Step 4: Find additional profiles
  const socialProfiles = await findSocialProfiles(baseData.profile_name);

  // Step 5: Compile prospect intelligence
  return {
    ...baseData,
    enriched_data: {
      tech_stack: companyData.tech_stack,
      funding: companyData.funding,
      recent_news: exaData.news,
      github_url: socialProfiles.github,
      twitter_url: socialProfiles.twitter,
      personal_website: socialProfiles.website,
      pain_points: identifyPainPoints(companyData, exaData),
      personalization_hooks: generateHooks(baseData, companyData, exaData)
    }
  };
}
```

## Anti-Spam Techniques

### 1. **Interaction History Check**
Before any outreach, check if you've already contacted them:

```javascript
async function checkInteractionHistory(linkedinUrl) {
  const history = await getLookbackHistory(linkedinUrl);

  if (history.connection_request_sent) {
    return {
      proceed: false,
      reason: 'Already sent connection request',
      last_contact: history.connection_request_date
    };
  }

  if (history.messages_sent >= 2 && !history.reply_received) {
    return {
      proceed: false,
      reason: 'Already sent 2 messages with no reply',
      last_contact: history.last_message_date
    };
  }

  const daysSinceLastContact = daysBetween(
    new Date(),
    new Date(history.last_interaction)
  );

  if (daysSinceLastContact < 30) {
    return {
      proceed: false,
      reason: 'Too soon after last contact',
      last_contact: history.last_interaction
    };
  }

  return { proceed: true };
}
```

### 2. **Duplicate Prevention**
Prevent sending multiple requests to same person:

```javascript
// Before sending connection request
const existing = await checkExistingConnection(profile.linkedin_url);
if (existing.is_connected) {
  console.log('Already connected, skipping');
  return;
}
if (existing.request_pending) {
  console.log('Connection request pending, skipping');
  return;
}
```

### 3. **Response Tracking**
Track who responds to optimize strategy:

```javascript
// After message sent
await trackOutreach({
  linkedin_url: profile.url,
  message_type: 'connection_request',
  sent_at: new Date(),
  template_id: template.id
});

// After reply received
await trackResponse({
  linkedin_url: profile.url,
  replied_at: new Date(),
  time_to_response: daysSinceSent,
  positive_response: true // manual classification
});

// Analyze what works
const bestTemplates = await getTopPerformingTemplates();
const bestSendTimes = await getBestSendTimes();
const bestFollowupDelay = await getOptimalFollowupDelay();
```

## Metrics to Track

### Activity Metrics
- Profile views per day
- Connection requests sent
- Connections accepted
- Messages sent
- Messages replied to

### Engagement Metrics
- Connection acceptance rate
- Message response rate
- Time to first response
- Conversation duration
- Meeting booking rate

### Business Metrics
- Leads generated
- Opportunities created
- Pipeline value
- Closed deals
- ROI per channel

### Quality Metrics
- ICP match rate
- Lead score distribution
- Account restrictions (should be 0)
- Spam reports (should be 0)
- Unsubscribe rate

## Dashboard Setup

Create a monitoring dashboard with:

```javascript
// Real-time activity monitor
{
  today: {
    profile_views: 45,
    connections_sent: 12,
    messages_sent: 8,
    replies_received: 3
  },
  limits: {
    connections: {
      used: 12,
      limit: 15,
      remaining: 3
    },
    messages: {
      used: 8,
      limit: 40,
      remaining: 32
    }
  },
  acceptance_rate: {
    last_7_days: 0.34, // 34%
    last_30_days: 0.29, // 29%
    trend: 'up'
  },
  top_performing: {
    templates: [
      { id: 't1', name: 'Industry Leader', acceptance: 0.42 },
      { id: 't2', name: 'Mutual Connection', acceptance: 0.38 }
    ],
    times: [
      { hour: 9, acceptance: 0.41 },
      { hour: 17, acceptance: 0.36 }
    ]
  }
}
```

## Compliance & Ethics

### Do's
- ✅ Use real profile and information
- ✅ Personalize every message
- ✅ Provide value in every interaction
- ✅ Respect opt-outs immediately
- ✅ Track and honor rate limits
- ✅ Be transparent about your intent
- ✅ Follow up appropriately
- ✅ Build genuine relationships

### Don'ts
- ❌ Scrape data aggressively
- ❌ Send generic spam messages
- ❌ Ignore connection degree
- ❌ Use fake profiles or information
- ❌ Bypass rate limits
- ❌ Continue after rejection
- ❌ Buy connection lists
- ❌ Violate LinkedIn terms

## Troubleshooting Guide

### Low Acceptance Rate (<20%)
**Causes:**
- Poor targeting (wrong ICP)
- Generic messages
- Suspicious profile (incomplete, no photo)
- Wrong connection degree (3rd only)

**Solutions:**
- Improve ICP targeting
- Add personalization hooks
- Complete your profile (photo, headline, summary)
- Focus on 1st and 2nd degree connections

### Low Response Rate (<10%)
**Causes:**
- Messages too salesy
- No clear value proposition
- Poor timing
- Wrong audience

**Solutions:**
- Lead with value, not pitch
- Ask questions
- Send during business hours
- Re-qualify leads

### Account Restrictions
**Causes:**
- Exceeded rate limits
- Too many spam reports
- Bot-like behavior
- Aggressive automation

**Solutions:**
- Stop automation immediately
- Review and lower limits
- Add more randomization
- Improve message quality
- Wait for restriction to lift

## Resources

- LinkedIn Lookback: [./linkedin-rate-limits.md](./linkedin-rate-limits.md)
- Personalization Examples: [./message-templates.md](./message-templates.md)
- Exa AI Documentation: https://docs.exa.ai
- 10x-Team Workflows: `../../workflows/`

---

**Last Updated:** 2026-01-22
**Version:** 1.0.0
**Next Review:** 2026-04-22
