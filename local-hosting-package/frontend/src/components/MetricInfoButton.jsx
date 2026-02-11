import { useState } from "react";
import { Info, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

/**
 * MetricInfoButton - Info button that shows formula and explanation for metrics
 */
const MetricInfoButton = ({ 
  metricKey, 
  className,
  size = "sm",
  variant = "ghost"
}) => {
  const [open, setOpen] = useState(false);
  const info = getMetricInfo(metricKey);

  if (!info) return null;

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={cn(
          "h-5 w-5 p-0 rounded-full",
          "text-slate-400 hover:text-slate-600",
          "hover:bg-slate-100",
          className
        )}
        onClick={(e) => {
          e.stopPropagation();
          setOpen(true);
        }}
        title={`Formula for ${info.title}`}
      >
        <Info className="w-3.5 h-3.5" strokeWidth={2.5} />
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="text-xl font-bold">
                {info.title}
              </DialogTitle>
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                onClick={() => setOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <DialogDescription className="text-base pt-2">
              {info.description}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 pt-4">
            {/* Formula Section */}
            {info.formula && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="font-mono text-xs">
                    Formula
                  </Badge>
                </div>
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 border border-slate-200 dark:border-slate-700">
                  <code className="text-sm font-mono text-slate-900 dark:text-slate-100 whitespace-pre-wrap">
                    {info.formula}
                  </code>
                </div>
              </div>
            )}

            {/* Calculation Steps */}
            {info.calculationSteps && info.calculationSteps.length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-slate-700 dark:text-slate-300">
                  Calculation Steps:
                </h4>
                <ol className="list-decimal list-inside space-y-1.5 text-sm text-slate-600 dark:text-slate-400">
                  {info.calculationSteps.map((step, idx) => (
                    <li key={idx} className="pl-2">{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {/* Variables Explanation */}
            {info.variables && Object.keys(info.variables).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-slate-700 dark:text-slate-300">
                  Variables:
                </h4>
                <div className="space-y-2">
                  {Object.entries(info.variables).map(([key, desc]) => (
                    <div key={key} className="flex gap-3">
                      <code className="text-xs font-mono bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded flex-shrink-0">
                        {key}
                      </code>
                      <span className="text-sm text-slate-600 dark:text-slate-400 flex-1">
                        {desc}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <Separator />

            {/* Additional Notes */}
            {info.notes && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-slate-700 dark:text-slate-300">
                  Notes:
                </h4>
                <ul className="list-disc list-inside space-y-1 text-sm text-slate-600 dark:text-slate-400">
                  {info.notes.map((note, idx) => (
                    <li key={idx} className="pl-2">{note}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Example */}
            {info.example && (
              <div className="space-y-2">
                <h4 className="font-semibold text-sm text-slate-700 dark:text-slate-300">
                  Example:
                </h4>
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    {info.example}
                  </p>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

/**
 * Centralized metric information database
 */
const METRIC_INFO = {
  // Executive Dashboard
  "school_health_index": {
    title: "School Health Index (SHI)",
    description: "Composite index measuring overall school health across multiple domains",
    formula: "SHI = (Identity × 0.25) + (Infrastructure × 0.25) + (Teacher × 0.25) + (Operational × 0.25)",
    calculationSteps: [
      "Calculate domain indices for Identity, Infrastructure, Teacher, and Operational",
      "Each domain index is normalized to 0-100 scale",
      "Apply weighted average with equal weights (25% each)",
      "Result is rounded to 1 decimal place"
    ],
    variables: {
      "Identity": "Student Identity domain index (Aadhaar + APAAR metrics)",
      "Infrastructure": "Infrastructure & Facilities domain index",
      "Teacher": "Teacher & Staffing domain index",
      "Operational": "Operational Performance domain index"
    },
    notes: [
      "SHI ranges from 0 to 100",
      "Green: ≥85, Amber: 70-84, Red: <70",
      "All domains have equal weight in the calculation"
    ],
    example: "If Identity=80, Infrastructure=75, Teacher=90, Operational=85, then SHI = (80×0.25) + (75×0.25) + (90×0.25) + (85×0.25) = 82.5"
  },

  "student_identity_domain_index": {
    title: "Student Identity Domain Index",
    description: "Composite index measuring student identity verification and compliance",
    formula: "Identity Index = (Aadhaar% × 0.4) + (APAAR% × 0.4) + ((100 - NameMismatch%) × 0.2)",
    calculationSteps: [
      "Calculate Aadhaar coverage percentage (Verified Aadhaar / Total Students × 100)",
      "Calculate APAAR generation percentage (Generated APAAR / Total Students × 100)",
      "Calculate name mismatch rate (Name Mismatches / Total Students × 100)",
      "Apply weighted formula: Aadhaar (40%) + APAAR (40%) + Name Accuracy (20%)",
      "Result is rounded to 1 decimal place"
    ],
    variables: {
      "Aadhaar%": "Percentage of students with verified Aadhaar numbers",
      "APAAR%": "Percentage of students with generated APAAR IDs",
      "NameMismatch%": "Percentage of students with name mismatches between records"
    },
    notes: [
      "Index ranges from 0 to 100",
      "Higher values indicate better identity compliance",
      "Name mismatch is inverted (100 - mismatch%) to contribute positively",
      "Aadhaar and APAAR have equal weight (40% each)"
    ],
    example: "If Aadhaar=85%, APAAR=75%, NameMismatch=5%, then Identity Index = (85×0.4) + (75×0.4) + ((100-5)×0.2) = 34 + 30 + 19 = 83.0"
  },

  "infrastructure_domain_index": {
    title: "Infrastructure Domain Index",
    description: "Composite index measuring school infrastructure quality and facilities",
    formula: "Infrastructure Index = (Classroom Health × 0.3) + (Toilet Functional × 0.25) + (Water Availability × 0.25) + (Electricity × 0.2)",
    calculationSteps: [
      "Calculate Classroom Health % (Functional Classrooms / Required Classrooms × 100)",
      "Calculate Toilet Functional % (Functional Toilets / Total Toilets × 100)",
      "Calculate Water Availability % (Schools with Water / Total Schools × 100)",
      "Calculate Electricity % (Schools with Electricity / Total Schools × 100)",
      "Apply weighted formula with specified weights",
      "Result is rounded to 1 decimal place"
    ],
    variables: {
      "Classroom Health": "Percentage of functional classrooms relative to required",
      "Toilet Functional": "Percentage of functional toilets",
      "Water Availability": "Percentage of schools with functional water supply",
      "Electricity": "Percentage of schools with electricity connection"
    },
    notes: [
      "Index ranges from 0 to 100",
      "Classroom Health has the highest weight (30%)",
      "Toilet and Water have equal weight (25% each)",
      "Electricity contributes 20%"
    ],
    example: "If Classroom=80%, Toilet=90%, Water=85%, Electricity=95%, then Infrastructure Index = (80×0.3) + (90×0.25) + (85×0.25) + (95×0.2) = 24 + 22.5 + 21.25 + 19 = 86.75"
  },

  "teacher_quality_domain_index": {
    title: "Teacher Quality Domain Index",
    description: "Composite index measuring teacher qualifications, training, and verification",
    formula: "Teacher Quality Index = (CTET% × 0.4) + (NISHTHA% × 0.3) + (Aadhaar Verified% × 0.3)",
    calculationSteps: [
      "Calculate CTET qualified percentage (CTET Qualified Teachers / Total Teachers × 100)",
      "Calculate NISHTHA training percentage (NISHTHA Trained Teachers / Total Teachers × 100)",
      "Calculate Aadhaar verified percentage (Aadhaar Verified Teachers / Total Teachers × 100)",
      "Apply weighted formula: CTET (40%) + NISHTHA (30%) + Aadhaar (30%)",
      "Result is rounded to 1 decimal place"
    ],
    variables: {
      "CTET%": "Percentage of teachers qualified with CTET (Central Teacher Eligibility Test)",
      "NISHTHA%": "Percentage of teachers who completed NISHTHA training",
      "Aadhaar Verified%": "Percentage of teachers with verified Aadhaar numbers"
    },
    notes: [
      "Index ranges from 0 to 100",
      "CTET qualification has the highest weight (40%)",
      "NISHTHA training and Aadhaar verification have equal weight (30% each)",
      "Higher index indicates better teacher quality and compliance"
    ],
    example: "If CTET=70%, NISHTHA=80%, Aadhaar=90%, then Teacher Quality Index = (70×0.4) + (80×0.3) + (90×0.3) = 28 + 24 + 27 = 79.0"
  },

  "operational_domain_index": {
    title: "Operational Domain Index",
    description: "Composite index measuring operational efficiency and data quality",
    formula: "Operational Index = (Completion Rate × 0.3) + (Certification Rate × 0.25) + (Data Accuracy × 0.25) + ((100 - Dropout Rate) × 0.2)",
    calculationSteps: [
      "Calculate Data Entry Completion Rate (Completed Records / Total Records × 100)",
      "Calculate School Certification Rate (Certified Schools / Total Schools × 100)",
      "Calculate Data Accuracy Rate ((Total Remarks - Wrong Entries) / Total Remarks × 100)",
      "Calculate Dropout Rate (Dropout Count / Total Remarks × 100)",
      "Apply weighted formula: Completion (30%) + Certification (25%) + Accuracy (25%) + Retention (20%)",
      "Dropout rate is inverted (100 - dropout%) to contribute positively",
      "Result is rounded to 1 decimal place"
    ],
    variables: {
      "Completion Rate": "Percentage of student records with completed data entry",
      "Certification Rate": "Percentage of schools with certified data",
      "Data Accuracy": "Percentage of accurate records (excluding wrong entries)",
      "Dropout Rate": "Percentage of students who dropped out"
    },
    notes: [
      "Index ranges from 0 to 100",
      "Completion Rate has the highest weight (30%)",
      "Certification and Data Accuracy have equal weight (25% each)",
      "Dropout rate is inverted so lower dropout contributes more to the index",
      "Higher index indicates better operational performance"
    ],
    example: "If Completion=85%, Certification=80%, Data Accuracy=90%, Dropout=10%, then Operational Index = (85×0.3) + (80×0.25) + (90×0.25) + ((100-10)×0.2) = 25.5 + 20 + 22.5 + 18 = 86.0"
  },

  // Student Identity Metrics
  "aadhaar_verification_rate": {
    title: "Aadhaar Verification Rate",
    description: "Percentage of students with verified Aadhaar numbers",
    formula: "Aadhaar Rate = (Verified Aadhaar Students / Total Students) × 100",
    calculationSteps: [
      "Count total number of students in scope",
      "Count students with verified Aadhaar status",
      "Divide verified by total and multiply by 100",
      "Round to 2 decimal places"
    ],
    variables: {
      "Verified Aadhaar Students": "Number of students with Aadhaar verification status = 'Verified'",
      "Total Students": "Total number of enrolled students in the selected scope"
    },
    notes: [
      "Verification status must be exactly 'Verified'",
      "Includes all students regardless of class or age"
    ],
    example: "If 50,000 students have verified Aadhaar out of 60,000 total students, rate = (50,000/60,000) × 100 = 83.33%"
  },

  "apaar_generation_rate": {
    title: "APAAR Generation Rate",
    description: "Percentage of students with generated APAAR IDs",
    formula: "APAAR Rate = (Generated APAAR IDs / Total Students) × 100",
    calculationSteps: [
      "Count total number of students",
      "Count students with APAAR status = 'Generated'",
      "Calculate percentage",
      "Round to 2 decimal places"
    ],
    variables: {
      "Generated APAAR IDs": "Number of students with APAAR status = 'Generated'",
      "Total Students": "Total enrolled students in scope"
    },
    notes: [
      "APAAR status must be 'Generated' (not 'Requested' or 'Failed')",
      "Pending applications are not counted as generated"
    ]
  },

  // Infrastructure Metrics
  "classroom_health": {
    title: "Classroom Health Index",
    description: "Measure of classroom adequacy and functionality",
    formula: "Classroom Health = (Functional Classrooms / Required Classrooms) × 100",
    calculationSteps: [
      "Calculate required classrooms based on student-teacher ratio (30:1)",
      "Count functional/available classrooms",
      "Divide functional by required and multiply by 100",
      "Cap at 100% if functional exceeds required"
    ],
    variables: {
      "Functional Classrooms": "Number of classrooms that are usable and functional",
      "Required Classrooms": "Total classrooms needed based on enrollment and ratio standards"
    },
    notes: [
      "Standard ratio: 30 students per classroom",
      "Values above 100% indicate surplus capacity"
    ]
  },

  "toilet_functional_rate": {
    title: "Functional Toilet Rate",
    description: "Percentage of schools with functional toilet facilities",
    formula: "Functional Toilet Rate = (Schools with Functional Toilets / Total Schools) × 100",
    calculationSteps: [
      "Count total schools in scope",
      "Count schools where toilet_status = 'Functional'",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Schools with Functional Toilets": "Schools where toilets are operational and usable",
      "Total Schools": "Total number of schools in selected scope"
    },
    notes: [
      "Both boys and girls toilets must be functional",
      "Non-functional includes under-construction and damaged toilets"
    ]
  },

  // Teacher Metrics
  "teacher_student_ratio": {
    title: "Teacher-Student Ratio",
    description: "Average number of students per teacher",
    formula: "Teacher-Student Ratio = Total Students / Total Teachers",
    calculationSteps: [
      "Sum all enrolled students in scope",
      "Sum all active teachers in scope",
      "Divide students by teachers",
      "Round to 2 decimal places"
    ],
    variables: {
      "Total Students": "Total enrolled students across all classes",
      "Total Teachers": "Total active/working teachers (excluding vacant positions)"
    },
    notes: [
      "Standard ratio: 30:1 (30 students per teacher)",
      "Lower ratio indicates better teacher availability",
      "Includes all subject teachers and class teachers"
    ]
  },

  "teacher_attendance_rate": {
    title: "Teacher Attendance Rate",
    description: "Percentage of teachers with good attendance records",
    formula: "Attendance Rate = (Teachers with Attendance ≥ 75% / Total Teachers) × 100",
    calculationSteps: [
      "Count total teachers",
      "Count teachers with attendance percentage ≥ 75%",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Teachers with Attendance ≥ 75%": "Teachers meeting minimum attendance threshold",
      "Total Teachers": "All active teachers in the scope"
    },
    notes: [
      "Minimum threshold: 75% attendance",
      "Based on monthly attendance records"
    ]
  },

  // Operational Metrics
  "data_entry_completion_rate": {
    title: "Data Entry Completion Rate",
    description: "Percentage of student records with completed data entry",
    formula: "Completion Rate = (Completed Records / Total Records) × 100",
    calculationSteps: [
      "Count total student records",
      "Count records with status = 'Completed'",
      "Calculate percentage",
      "Round to 2 decimal places"
    ],
    variables: {
      "Completed Records": "Student records with all required fields filled",
      "Total Records": "Total number of student records in the system"
    },
    notes: [
      "Includes all mandatory fields: name, DOB, class, enrollment details",
      "Pending and in-progress records are not counted as completed"
    ]
  },

  "certification_rate": {
    title: "School Certification Rate",
    description: "Percentage of schools with certified data",
    formula: "Certification Rate = (Certified Schools / Total Schools) × 100",
    calculationSteps: [
      "Count total schools",
      "Count schools with certified = 'Yes'",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Certified Schools": "Schools where data has been verified and certified",
      "Total Schools": "Total number of schools in scope"
    },
    notes: [
      "Certification requires data verification by authorized personnel",
      "Only 'Yes' status is counted as certified"
    ]
  },

  "dropout_rate": {
    title: "Student Dropout Rate",
    description: "Percentage of students who dropped out",
    formula: "Dropout Rate = (Dropout Count / Total Remarks) × 100",
    calculationSteps: [
      "Count total remarks/records in dropbox data",
      "Count records with dropout = true or dropout_count > 0",
      "Calculate percentage",
      "Round to 2 decimal places"
    ],
    variables: {
      "Dropout Count": "Number of students who dropped out",
      "Total Remarks": "Total number of remarks/records in dropbox analytics"
    },
    notes: [
      "Based on dropbox remarks data",
      "Includes all dropout reasons: migration, death, irregular attendance, etc."
    ]
  },

  // Enrolment Metrics
  "girls_enrolment_percentage": {
    title: "Girls Enrolment Percentage",
    description: "Percentage of female students in total enrolment",
    formula: "Girls % = (Girls Enrolment / Total Enrolment) × 100",
    calculationSteps: [
      "Sum total enrolment across all classes",
      "Sum girls enrolment across all classes",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Girls Enrolment": "Total number of female students enrolled",
      "Total Enrolment": "Total number of students (boys + girls) enrolled"
    },
    notes: [
      "Includes all classes from 1 to 12",
      "Gender is determined from student records"
    ]
  },

  // Teacher Quality Metrics
  "retirement_risk": {
    title: "Retirement Risk Percentage",
    description: "Percentage of teachers approaching retirement age (55 years and above)",
    formula: "Retirement Risk % = (Teachers Aged ≥ 55 Years / Total Teachers) × 100",
    calculationSteps: [
      "Count total number of teachers in scope",
      "Count teachers with age ≥ 55 years",
      "Divide retirement-risk teachers by total teachers",
      "Multiply by 100 to get percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Teachers Aged ≥ 55 Years": "Number of teachers who are 55 years old or older",
      "Total Teachers": "Total number of active teachers in the selected scope"
    },
    notes: [
      "Retirement age in India is typically 58-60 years for teachers",
      "Teachers aged 55+ are considered at high risk of retirement within 3-5 years",
      "This metric helps in workforce planning and recruitment",
      "Based on teacher age field in the database"
    ],
    example: "If there are 7,998 teachers aged 55+ out of 77,389 total teachers, Retirement Risk = (7,998 / 77,389) × 100 = 10.3%"
  },

  "female_representation": {
    title: "Female Representation Percentage",
    description: "Percentage of female teachers in the total teaching workforce",
    formula: "Female Representation % = (Female Teachers / Total Teachers) × 100",
    calculationSteps: [
      "Count total number of teachers in scope",
      "Count teachers with gender = '2-Female' or 'Female'",
      "Divide female teachers by total teachers",
      "Multiply by 100 to get percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Female Teachers": "Number of teachers identified as female (gender = '2-Female' or 'Female')",
      "Total Teachers": "Total number of active teachers in the selected scope"
    },
    notes: [
      "Gender is determined from the gender field in teacher records",
      "Values can be '1-Male', '2-Female', or '3-Transgender'",
      "Higher female representation indicates better gender diversity in teaching staff",
      "This metric is important for gender parity and inclusive education",
      "The calculation includes all teacher records, not unique teachers"
    ],
    example: "If there are 57,191 female teachers out of 77,389 total teachers, Female Representation = (57,191 / 77,389) × 100 = 73.9%"
  },

  "repeater_rate": {
    title: "Repeater Rate",
    description: "Percentage of students repeating the same class",
    formula: "Repeater Rate = (Repeaters / Total Students) × 100",
    calculationSteps: [
      "Count total students",
      "Count students with repeater status = true",
      "Calculate percentage",
      "Round to 2 decimal places"
    ],
    variables: {
      "Repeaters": "Students repeating the same class",
      "Total Students": "Total enrolled students"
    },
    notes: [
      "Repeaters are students enrolled in the same class for consecutive years",
      "Lower rate indicates better academic progression"
    ]
  },

  // Age-wise Enrolment
  "age_appropriate_enrolment": {
    title: "Age-Appropriate Enrolment Rate",
    description: "Percentage of students enrolled in age-appropriate classes",
    formula: "Age-Appropriate Rate = (Age-Appropriate Students / Total Students) × 100",
    calculationSteps: [
      "Determine expected class for each student based on age",
      "Count students in expected class",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Age-Appropriate Students": "Students enrolled in class matching their age",
      "Total Students": "Total enrolled students"
    },
    notes: [
      "Standard: Class 1 at age 6, Class 2 at age 7, etc.",
      "±1 year variance is considered acceptable"
    ]
  },

  // CTTeacher Metrics
  "ctet_qualified_percentage": {
    title: "CTET Qualified Teacher Percentage",
    description: "Percentage of teachers qualified with CTET certification",
    formula: "CTET % = (CTET Qualified Teachers / Total Teachers) × 100",
    calculationSteps: [
      "Count total teachers",
      "Count teachers with CTET qualification = 'Yes'",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "CTET Qualified Teachers": "Teachers with CTET (Central Teacher Eligibility Test) certification",
      "Total Teachers": "Total number of teachers in scope"
    },
    notes: [
      "CTET is mandatory for teaching positions in government schools",
      "Includes both Paper I and Paper II qualified teachers"
    ]
  },

  "ctet_qualified": {
    title: "CTET Qualified Percentage",
    description: "Percentage of teachers qualified with CTET (Central Teacher Eligibility Test) certification",
    formula: "CTET % = (CTET Qualified Teachers / Total Teachers) × 100",
    calculationSteps: [
      "Count total number of teachers in scope",
      "Count teachers with ctet_qualified = 1 (Yes)",
      "Divide CTET qualified by total teachers",
      "Multiply by 100 to get percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "CTET Qualified Teachers": "Number of teachers with CTET certification (ctet_qualified = 1)",
      "Total Teachers": "Total number of active teachers in the selected scope"
    },
    notes: [
      "CTET is mandatory for teaching positions in government schools",
      "Includes both Paper I (for classes 1-5) and Paper II (for classes 6-8) qualified teachers",
      "Higher percentage indicates better teacher qualification standards"
    ],
    example: "If 5,000 teachers are CTET qualified out of 77,389 total teachers, CTET % = (5,000 / 77,389) × 100 = 6.5%"
  },

  "nishtha_completed": {
    title: "NISHTHA Training Completion Percentage",
    description: "Percentage of teachers who have completed NISHTHA (National Initiative for School Heads' and Teachers' Holistic Advancement) training",
    formula: "NISHTHA % = (NISHTHA Completed Teachers / Total Teachers) × 100",
    calculationSteps: [
      "Count total number of teachers in scope",
      "Count teachers with training_nishtha = 1 (Yes)",
      "Divide NISHTHA completed by total teachers",
      "Multiply by 100 to get percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "NISHTHA Completed Teachers": "Number of teachers who completed NISHTHA training (training_nishtha = 1)",
      "Total Teachers": "Total number of active teachers in the selected scope"
    },
    notes: [
      "NISHTHA is a capacity building program for teachers and school heads",
      "Training completion is tracked through the training_nishtha field",
      "Higher percentage indicates better teacher training coverage"
    ],
    example: "If 25,000 teachers completed NISHTHA out of 77,389 total teachers, NISHTHA % = (25,000 / 77,389) × 100 = 32.3%"
  },

  "teacher_aadhaar_verified": {
    title: "Teacher Aadhaar Verification Percentage",
    description: "Percentage of teachers with verified Aadhaar numbers through UIDAI",
    formula: "Aadhaar Verified % = (Aadhaar Verified Teachers / Total Teachers) × 100",
    calculationSteps: [
      "Count total number of teachers in scope",
      "Count teachers with aadhaar_verified = 'Verified From UIDAI against Name,Gender & DOB'",
      "Divide verified teachers by total teachers",
      "Multiply by 100 to get percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Aadhaar Verified Teachers": "Number of teachers with verified Aadhaar (status = 'Verified From UIDAI against Name,Gender & DOB')",
      "Total Teachers": "Total number of active teachers in the selected scope"
    },
    notes: [
      "Aadhaar verification is done through UIDAI (Unique Identification Authority of India)",
      "Verification status can be: 'Verified From UIDAI against Name,Gender & DOB', 'Verification Failed From UIDAI', or 'Verification Under Process'",
      "Only 'Verified From UIDAI against Name,Gender & DOB' status is counted as verified",
      "Higher percentage indicates better identity verification compliance"
    ],
    example: "If 72,118 teachers have verified Aadhaar out of 77,389 total teachers, Aadhaar Verified % = (72,118 / 77,389) × 100 = 93.2%"
  },

  // Data Entry Metrics
  "pending_data_entry": {
    title: "Pending Data Entry",
    description: "Number of student records pending data entry",
    formula: "Pending = Not Started + In Progress",
    calculationSteps: [
      "Count records with status = 'Not Started'",
      "Count records with status = 'In Progress'",
      "Sum both counts"
    ],
    variables: {
      "Not Started": "Records where data entry has not begun",
      "In Progress": "Records where data entry is partially complete"
    },
    notes: [
      "Does not include completed records",
      "Lower value indicates better data entry progress"
    ]
  },

  // Dropbox Metrics
  "data_accuracy": {
    title: "Data Accuracy Rate",
    description: "Percentage of accurate records (excluding wrong entries)",
    formula: "Data Accuracy = ((Total Remarks - Wrong Entries) / Total Remarks) × 100",
    calculationSteps: [
      "Count total remarks/records",
      "Count wrong_entry records",
      "Subtract wrong entries from total",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Total Remarks": "Total number of remarks/records",
      "Wrong Entries": "Records marked as incorrect or erroneous"
    },
    notes: [
      "Higher accuracy indicates better data quality",
      "Wrong entries include data entry errors and corrections"
    ]
  },

  // Infrastructure Metrics
  "water_availability": {
    title: "Water Availability Rate",
    description: "Percentage of schools with functional water supply",
    formula: "Water Availability = (Schools with Water / Total Schools) × 100",
    calculationSteps: [
      "Count total schools",
      "Count schools with water_status = 'Available'",
      "Calculate percentage",
      "Round to 1 decimal place"
    ],
    variables: {
      "Schools with Water": "Schools with functional water supply",
      "Total Schools": "Total number of schools"
    },
    notes: [
      "Includes both drinking water and general water supply",
      "Functional means water is available and accessible"
    ]
  },

  // General Metrics
  "total_schools": {
    title: "Total Schools",
    description: "Total number of schools in the selected scope",
    formula: "Total Schools = Count of distinct schools",
    calculationSteps: [
      "Apply scope filters (district, block, school)",
      "Count distinct schools matching the scope",
      "Return the count"
    ],
    variables: {
      "Scope": "Selected filters: district, block, or school level"
    },
    notes: [
      "Count is based on UDISE codes (unique school identifiers)",
      "Includes all schools matching the current scope"
    ]
  },

  "total_students": {
    title: "Total Students",
    description: "Total number of enrolled students",
    formula: "Total Students = Sum of all enrolled students",
    calculationSteps: [
      "Apply scope filters",
      "Sum student counts across all schools in scope",
      "Return the total"
    ],
    variables: {
      "Enrolled Students": "Students currently enrolled in any class"
    },
    notes: [
      "Includes all classes from 1 to 12",
      "Excludes dropped out or migrated students"
    ]
  },

  "total_teachers": {
    title: "Total Teachers",
    description: "Total number of active teachers",
    formula: "Total Teachers = Sum of all active teachers",
    calculationSteps: [
      "Apply scope filters",
      "Count active teachers (excluding vacant positions)",
      "Return the total"
    ],
    variables: {
      "Active Teachers": "Teachers currently working and assigned to schools"
    },
    notes: [
      "Excludes vacant teaching positions",
      "Includes all subject teachers and class teachers"
    ]
  }
};

/**
 * Get metric information by key
 */
export function getMetricInfo(metricKey) {
  return METRIC_INFO[metricKey] || null;
}

/**
 * Get all available metric keys
 */
export function getAllMetricKeys() {
  return Object.keys(METRIC_INFO);
}

export default MetricInfoButton;

