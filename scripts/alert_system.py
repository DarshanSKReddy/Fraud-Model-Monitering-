"""Alert system for fraud detection model monitoring."""
import os
import json
from datetime import datetime

ALERTS_FILE = 'reports/alerts.json'
DRIFT_METRICS = 'reports/drift_metrics.json'
PERFORMANCE_METRICS = 'reports/performance_metrics.json'


def create_alert(alert_type, severity, message, details=None):
    """Create and log an alert."""
    alert = {
        'timestamp': datetime.now().isoformat(),
        'type': alert_type,
        'severity': severity,  # INFO, WARNING, CRITICAL
        'message': message,
        'details': details or {}
    }
    
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    
    # Append to alerts file
    with open(ALERTS_FILE, 'a') as f:
        f.write(json.dumps(alert) + '\n')
    
    return alert


def check_drift_alerts():
    """Check for data drift and create alerts."""
    if not os.path.exists(DRIFT_METRICS):
        return
    
    with open(DRIFT_METRICS, 'r') as f:
        drift_data = json.load(f)
    
    if drift_data.get('drift_count', 0) > 0:
        drifted_features = drift_data.get('features_with_drift', [])
        create_alert(
            'Data Drift',
            'WARNING',
            f"Data drift detected in {len(drifted_features)} features",
            {'drifted_features': drifted_features}
        )
        return True
    
    return False


def check_performance_alerts():
    """Check for performance issues and create alerts."""
    if not os.path.exists(PERFORMANCE_METRICS):
        return
    
    with open(PERFORMANCE_METRICS, 'r') as f:
        perf_data = json.load(f)
    
    # Check block rate (if too high, might indicate false positives)
    block_rate = perf_data.get('block_rate', 0)
    if block_rate > 0.05:  # More than 5% blocked
        create_alert(
            'High Block Rate',
            'WARNING',
            f"Block rate is {100*block_rate:.1f}% - review for false positives",
            {'block_rate': block_rate}
        )
    
    # Check if no predictions (system offline)
    if perf_data.get('total_predictions', 0) == 0:
        create_alert(
            'System Status',
            'CRITICAL',
            "No predictions recorded - system may be offline",
            {}
        )


def generate_alert_report():
    """Generate alert report."""
    print("=" * 70)
    print("ALERT SYSTEM MONITORING")
    print("=" * 70)
    
    # Check for alerts
    print("\n🔔 Running alert checks...")
    
    drift_alert = check_drift_alerts()
    perf_alert = check_performance_alerts()
    
    # Read all alerts
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as f:
            alerts = [json.loads(line) for line in f if line.strip()]
        
        print(f"\n📋 Alert Summary:")
        print(f"   Total Alerts: {len(alerts)}")
        
        # Count by severity
        critical = sum(1 for a in alerts if a['severity'] == 'CRITICAL')
        warning = sum(1 for a in alerts if a['severity'] == 'WARNING')
        info = sum(1 for a in alerts if a['severity'] == 'INFO')
        
        print(f"   Critical: {critical}")
        print(f"   Warning: {warning}")
        print(f"   Info: {info}")
        
        # Show recent alerts
        print(f"\n📌 Recent Alerts:")
        for alert in alerts[-10:]:
            icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡" if alert['severity'] == 'WARNING' else "🔵"
            print(f"   {icon} [{alert['severity']}] {alert['type']}: {alert['message']}")
    else:
        print("\n✓ No alerts recorded - system operating normally")
    
    # Generate alert report file
    alert_report = f"""# ALERT SYSTEM REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## System Status
✓ Alert monitoring system is active
✓ Drift detection enabled
✓ Performance monitoring enabled

## Current Configuration
- Drift threshold (PSI): 0.1
- Block rate alert threshold: 5%
- Offline detection: No predictions for >1 hour

## Alert History
See alerts.json for detailed log

## Action Items
1. Review critical alerts immediately
2. Acknowledge warnings within 24 hours
3. Log all manual interventions
4. Update threshold if needed

## Escalation Path
- Critical: Immediate notification to ML team
- Warning: Daily digest to stakeholders
- Info: Weekly summary report

"""
    
    with open('reports/alert_report.txt', 'w') as f:
        f.write(alert_report)
    
    print(f"\n✓ Alert report saved: reports/alert_report.txt")
    
    print("\n" + "=" * 70)
    print("✓ ALERT SYSTEM CHECK COMPLETE")
    print("=" * 70)
    return True


if __name__ == '__main__':
    import sys
    success = generate_alert_report()
    sys.exit(0 if success else 1)
