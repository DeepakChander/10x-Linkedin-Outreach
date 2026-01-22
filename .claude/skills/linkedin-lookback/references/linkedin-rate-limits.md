# LinkedIn Rate Limits & Best Practices

## Official LinkedIn Limits (2026)

### Connection Requests
- **Daily Limit**: 20-30 connection requests per day
- **Weekly Limit**: ~100 connection requests per week
- **Monthly Limit**: ~300-400 connection requests per month
- **Acceptance Rate Impact**: Low acceptance rates may reduce limits
- **Premium Accounts**: Slightly higher limits (30-40/day)

### Messages
- **Daily Limit**: 50-100 messages per day (Free accounts)
- **Premium/Sales Navigator**: 100-150 messages per day
- **InMail (Premium)**: 5-30 InMails per month (depends on plan)
- **Group Messages**: Unlimited to existing connections

### Profile Views
- **No Hard Limit**: LinkedIn encourages viewing profiles
- **Suspicious Activity**: Rapid viewing (100+/hour) may trigger warnings
- **Recommended**: 50-100 profile views per day
- **Best Practice**: Space out views (5-10 per hour)

### Searches
- **Free Account**: 3-5 searches per month with filters
- **Premium Account**: Unlimited commercial searches
- **Rate**: No more than 100 searches per hour

### Posts & Engagement
- **Posts**: 3-5 posts per day recommended
- **Comments**: 10-20 meaningful comments per day
- **Likes**: Unlimited (but avoid bot-like behavior)
- **Shares**: 5-10 per day recommended

## Safety Thresholds for Automation

### Conservative (Recommended)
```yaml
Connection Requests: 15/day
Messages: 40/day
Profile Views: 50/day
Searches: 20/day
```

### Moderate (For Established Accounts)
```yaml
Connection Requests: 20/day
Messages: 60/day
Profile Views: 80/day
Searches: 30/day
```

### Aggressive (Risk of Restrictions)
```yaml
Connection Requests: 25/day
Messages: 80/day
Profile Views: 100/day
Searches: 50/day
```

## Warning Signs

### Account Restrictions
- ⚠️ "Weekly invitation limit reached"
- ⚠️ "Too many pending invitations"
- ⚠️ "Unusual activity detected"
- ⚠️ Temporary profile view restrictions
- ⚠️ Message sending disabled

### How to Avoid Restrictions
1. **Space Out Actions**: Wait 30-60 seconds between actions
2. **Vary Patterns**: Don't automate exact same time every day
3. **High Acceptance Rate**: Target relevant prospects
4. **Personalize Messages**: Avoid copy-paste templates
5. **Engage Authentically**: Like, comment, share content
6. **Monitor Metrics**: Track acceptance and response rates

## Recovery from Restrictions

### Connection Request Limit Reached
- **Duration**: 7 days typically
- **Action**: Wait for the restriction to lift
- **Prevention**: Withdraw pending invitations (reduce to <100)
- **Future**: Lower daily connection request volume

### Message Restrictions
- **Duration**: 24-48 hours typically
- **Action**: Stop sending messages immediately
- **Prevention**: Reduce volume, increase personalization
- **Future**: Implement anti-spam best practices

### Account Suspension
- **Duration**: 7-30 days or permanent
- **Action**: Appeal via LinkedIn support
- **Causes**: Repeated violations, bot-like behavior, spam reports
- **Prevention**: Follow all guidelines strictly

## Best Practices for 10x-Team Integration

### 1. **Rate Limiting in Workflows**
```javascript
// Example: LinkedIn connection request workflow
const DAILY_CONNECTION_LIMIT = 15;
const HOURLY_CONNECTION_LIMIT = 5;
const DELAY_BETWEEN_REQUESTS = 60000; // 1 minute

// Check limits before sending
if (todayConnectionCount >= DAILY_CONNECTION_LIMIT) {
  throw new Error('Daily connection limit reached');
}

if (hourlyConnectionCount >= HOURLY_CONNECTION_LIMIT) {
  await sleep(3600000 - timeSinceLastRequest); // Wait until next hour
}

// Send connection request
await sendConnectionRequest(profile);
await sleep(DELAY_BETWEEN_REQUESTS); // Wait before next action
```

### 2. **Smart Scheduling**
- **Best Times**: 8-10 AM, 12-1 PM, 5-6 PM (local time)
- **Avoid**: Late night, early morning, weekends
- **Spread Actions**: Throughout the day (not all at once)
- **Time Zones**: Consider prospect's timezone

### 3. **Quality Signals**
```javascript
// Prioritize high-quality prospects
const qualityScore = calculateQualityScore({
  sharedConnections: profile.sharedConnections > 5 ? 10 : 0,
  inTargetIndustry: profile.industry === targetIndustry ? 10 : 0,
  seniorityLevel: profile.title.match(/Director|VP|C-Level/) ? 10 : 0,
  companySize: profile.companySize > 50 ? 5 : 0,
  recentActivity: profile.lastActiveWithin30Days ? 5 : 0
});

// Only send if quality score > threshold
if (qualityScore >= 25) {
  await sendConnectionRequest(profile);
}
```

### 4. **Acceptance Rate Monitoring**
```javascript
// Track acceptance rates
const acceptanceRate = acceptedConnections / sentConnections;

// Adjust strategy based on acceptance rate
if (acceptanceRate < 0.2) {
  // Low acceptance rate - reduce volume, improve targeting
  DAILY_CONNECTION_LIMIT = 10;
  qualityScoreThreshold = 30;
}

if (acceptanceRate > 0.5) {
  // High acceptance rate - can increase volume slightly
  DAILY_CONNECTION_LIMIT = 20;
  qualityScoreThreshold = 20;
}
```

### 5. **Humanization Techniques**
```javascript
// Add random delays to appear human
function getHumanizedDelay(baseDelay) {
  // Add ±30% randomization
  const randomFactor = 0.7 + Math.random() * 0.6;
  return baseDelay * randomFactor;
}

// Vary activity times
function getRandomActivityTime() {
  const hours = [8, 9, 10, 12, 13, 17]; // Active times
  const hour = hours[Math.floor(Math.random() * hours.length)];
  const minute = Math.floor(Math.random() * 60);
  return { hour, minute };
}

// Skip occasional days
function shouldSkipToday() {
  return Math.random() < 0.1; // Skip 10% of days randomly
}
```

## LinkedIn API vs Browser Automation

### Official LinkedIn API
- ✅ Safe and compliant
- ✅ No risk of restrictions
- ✅ Structured data access
- ❌ Limited functionality
- ❌ Requires approval
- ❌ Expensive ($$$)

### Browser Automation (Puppeteer/Browser-Use)
- ✅ Full LinkedIn functionality
- ✅ No API approval needed
- ✅ Cost-effective
- ⚠️ Risk of detection
- ⚠️ Must respect rate limits
- ⚠️ Requires careful implementation

### LinkedIn Lookback (Passive Tracking)
- ✅ Zero risk (passive only)
- ✅ No automation detection
- ✅ Tracks manual activity
- ❌ Requires manual LinkedIn use
- ❌ Not automated outreach
- ✅ Perfect for compliance

## Compliance Checklist

### Before Launching Automation
- [ ] Configured rate limits (conservative values)
- [ ] Implemented random delays
- [ ] Set up acceptance rate monitoring
- [ ] Added quality scoring system
- [ ] Created personalized message templates
- [ ] Tested with small batch (5-10 profiles)
- [ ] Reviewed LinkedIn Terms of Service
- [ ] Set up error handling and logging
- [ ] Implemented emergency stop mechanism
- [ ] Scheduled varied activity times

### During Automation
- [ ] Monitor daily metrics
- [ ] Track acceptance rates
- [ ] Watch for warning messages
- [ ] Adjust strategy based on data
- [ ] Maintain manual activity too
- [ ] Engage with content authentically
- [ ] Respond to messages promptly
- [ ] Review logs for anomalies

### If Restricted
- [ ] Stop all automation immediately
- [ ] Document what happened
- [ ] Wait for restriction to lift
- [ ] Review and adjust limits
- [ ] Improve targeting/personalization
- [ ] Test with lower volume
- [ ] Monitor closely after resuming

## Resources

- [LinkedIn Help: Connection Request Limits](https://www.linkedin.com/help/linkedin/answer/a1342460)
- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [LinkedIn Professional Community Policies](https://www.linkedin.com/help/linkedin/answer/a1342060)
- [Sales Navigator Rate Limits](https://www.linkedin.com/help/sales-navigator/answer/a120925)

## Updates

LinkedIn frequently updates their rate limiting algorithms. Always:
1. Monitor LinkedIn announcements
2. Check automation logs for errors
3. Adjust limits conservatively
4. Test new strategies with small batches
5. Follow community reports and discussions

---

**Last Updated:** 2026-01-22
**Version:** 1.0.0
**Next Review:** 2026-04-22
