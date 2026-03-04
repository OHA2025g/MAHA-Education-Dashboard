# 📊 Metric Info Buttons - Complete Guide

This guide explains how to add formula information buttons to all KPIs, metrics, and graphs in the dashboard.

## 🎯 Overview

Every KPI, metric, and graph can now display an information button (ℹ️) that shows:
- **Formula** used for calculation
- **Step-by-step calculation** process
- **Variable explanations**
- **Examples** with real numbers
- **Additional notes** and context

## 🚀 Quick Start

### For KPI Cards

Simply add the `metricKey` prop to any KPI card:

```jsx
import KPICard from "@/components/KPICard";
// or
import { EnhancedKPICard } from "@/components";

<KPICard
  label="Total Schools"
  value={7384}
  metricKey="total_schools"  // ← Add this
/>

<EnhancedKPICard
  label="Aadhaar Verification Rate"
  value={85.5}
  suffix="%"
  metricKey="aadhaar_verification_rate"  // ← Add this
/>
```

### For Charts/Graphs

Use `ChartInfoButton` component:

```jsx
import { ChartInfoButton } from "@/components";

<div className="relative">
  <ChartInfoButton 
    metricKey="school_health_index"
    position="top-right"
  />
  <BarChart>
    {/* Your chart */}
  </BarChart>
</div>
```

## 📋 Available Metric Keys

### Executive Dashboard
- `school_health_index` - School Health Index (SHI)
- `total_schools` - Total Schools
- `total_students` - Total Students
- `total_teachers` - Total Teachers

### Student Identity Metrics
- `aadhaar_verification_rate` - Aadhaar Verification Rate
- `apaar_generation_rate` - APAAR Generation Rate

### Infrastructure Metrics
- `classroom_health` - Classroom Health Index
- `toilet_functional_rate` - Functional Toilet Rate
- `water_availability` - Water Availability Rate

### Teacher Metrics
- `teacher_student_ratio` - Teacher-Student Ratio
- `teacher_attendance_rate` - Teacher Attendance Rate
- `ctet_qualified_percentage` - CTET Qualified Percentage

### Operational Metrics
- `data_entry_completion_rate` - Data Entry Completion Rate
- `certification_rate` - School Certification Rate
- `dropout_rate` - Student Dropout Rate
- `data_accuracy` - Data Accuracy Rate

### Enrolment Metrics
- `girls_enrolment_percentage` - Girls Enrolment Percentage
- `repeater_rate` - Repeater Rate
- `age_appropriate_enrolment` - Age-Appropriate Enrolment Rate

## 🔧 Adding New Metrics

To add a new metric to the database, edit `components/MetricInfoButton.jsx` and add to the `METRIC_INFO` object:

```jsx
const METRIC_INFO = {
  // ... existing metrics
  
  "your_metric_key": {
    title: "Your Metric Name",
    description: "Brief description of what this metric measures",
    formula: "Your Formula = (Variable1 / Variable2) × 100",
    calculationSteps: [
      "Step 1: Do this",
      "Step 2: Then do that",
      "Step 3: Finally calculate"
    ],
    variables: {
      "Variable1": "Explanation of variable 1",
      "Variable2": "Explanation of variable 2"
    },
    notes: [
      "Important note 1",
      "Important note 2"
    ],
    example: "If Variable1=100 and Variable2=200, then result = (100/200) × 100 = 50%"
  }
};
```

## 📝 Integration Examples

### Example 1: Executive Dashboard

```jsx
<KPICard
  label="School Health Index"
  value={shi.summary.school_health_index}
  suffix=""
  icon={Trophy}
  metricKey="school_health_index"  // ← Add this
/>
```

### Example 2: Aadhaar Dashboard

```jsx
<EnhancedKPICard
  label="Aadhaar Verification Rate"
  value={overview.aadhaar_rate}
  suffix="%"
  trend="up"
  trendValue="+2.5%"
  icon={ShieldCheck}
  color="green"
  gradient={true}
  metricKey="aadhaar_verification_rate"  // ← Add this
/>
```

### Example 3: Chart with Info Button

```jsx
<div className="relative">
  <ChartInfoButton 
    metricKey="teacher_student_ratio"
    position="top-right"
  />
  <ResponsiveContainer width="100%" height={300}>
    <BarChart data={chartData}>
      {/* Chart components */}
    </BarChart>
  </ResponsiveContainer>
</div>
```

## 🎨 Customization

### Button Position (for charts)
- `top-right` (default)
- `top-left`
- `bottom-right`
- `bottom-left`

### Button Variant
- `ghost` (default for KPICard)
- `outline` (for charts)

## 📚 Component API

### MetricInfoButton Props

```typescript
{
  metricKey: string;        // Required: Key from METRIC_INFO
  className?: string;       // Optional: Additional CSS classes
  size?: "sm" | "md" | "lg"; // Optional: Button size
  variant?: "ghost" | "outline" | "default"; // Optional: Button variant
}
```

### ChartInfoButton Props

```typescript
{
  metricKey: string;        // Required: Key from METRIC_INFO
  className?: string;       // Optional: Additional CSS classes
  position?: "top-right" | "top-left" | "bottom-right" | "bottom-left";
}
```

## 🔍 Finding the Right Metric Key

1. Check the `METRIC_INFO` object in `components/MetricInfoButton.jsx`
2. Use the key that matches your metric name (snake_case)
3. If not found, add a new entry following the structure above

## ✅ Best Practices

1. **Always add metricKey** to calculated metrics
2. **Use descriptive keys** that match the metric name
3. **Include all calculation steps** in the formula
4. **Provide examples** with realistic numbers
5. **Add notes** for important caveats or assumptions

## 🎯 Quick Reference

| Metric Type | Component | Prop to Add |
|------------|-----------|-------------|
| KPI Card | `KPICard` | `metricKey="..."` |
| Enhanced KPI | `EnhancedKPICard` | `metricKey="..."` |
| Chart/Graph | `ChartInfoButton` | `metricKey="..."` |

---

**Happy coding! 🚀**

