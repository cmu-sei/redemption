# How much SA should we do?

<legal>  
'Redemption' Automated Code Repair Tool  
  
Copyright 2023 Carnegie Mellon University.  
  
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING  
INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON  
UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,  
AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR  
PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF  
THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY  
KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT  
INFRINGEMENT.  
  
Licensed under a MIT (SEI)-style license, please see License.txt or  
contact permission@sei.cmu.edu for full terms.  
  
[DISTRIBUTION STATEMENT A] This material has been approved for public  
release and unlimited distribution.  Please see Copyright notice for  
non-US Government use and distribution.  
  
This Software includes and/or makes use of Third-Party Software each  
subject to its own license.  
  
DM23-2165  
</legal>  

This is best demonstrated by a question. Consider this code example:

``` c
void function() {
    int *array = malloc(sizeof(int) * 5);
    array[0] = 777;  // A
    0[array] = 999;  // B
    struct my_type *foo = malloc(sizeof(struct my_type));
    foo->i = 888;
    union my_union *bar = malloc(sizeof(union my_union));
    bar->i = 444;
    *array = 333;    // C
}
```

Suppose lines A, B, and C all trigger null-pointer dereference alerts. Which ones should we fix?  Everyone agrees that line A should be fixed (on the grounds that malloc() might have returned NULL). So should we fix line B? And what about line C?

Clearly, we can choose to fix each line, or we can choose not to.  If we don't fix either line, then we need to give reasons why.

A further question: suppose we fix only line A, rerun our SA tool, and it still says we must fix A, B, and C. Then what?

## The Human Answer

A human being would fix A, but leave B and C unfixed, on the grounds that the repair will cause function() to halt executing if array is NULL; and consequently lines B and C will not be executed. If lines B and C execute, then array must not be null, so no check is required.

In the [Audits: Lexicon and Rules"](https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=484185) paper, an audit would determine the alert on line A as True, and lines B and C as Dependent. This is because the alerts on lines B and C depend on whether the alert on line A is True or not.

## Static Analysis (SA)

The repair tool must perform some static analysis in order to do its work. Since the field of SA is well-established in industry, and because this is a research project, we want to limit the SA that our tool does.  Clearly, we need to determine that array must have the same value in lines A, B, and C, and use that to determine that only one repair is required at line A.

## Goals

  * Idempotent: ACR should repair code that it has already repaired. For example, line A should be repaired only once if ACR is run on the code twice.
  * Intelligent: ACR should repair the same subset of alerts that a human would repair.
  * Descriptive: If ACR does not repair an alert, it should provide a helpful reason why.

Here are some reasons not to repair code:

### Repair not Implemented

In an ideal world, this reason would never be given. In the real world, this reason may be because we don't know how to repair the code.  Given enough effort on this project, we can minimize the instances when this would happen. It is the goal of this project to restrict this error to under 20% of the total repairs for each rule. That is, only 1 out of every 5 null-pointer alerts should generate this reason.

### False

This reason means that ACR has enough SA wisdom to determine that the alert is a false positive, and the code does not violate the condition in question.  This also means that the tool that generated the alert is faulty or...well, stupid to generate it. Such faulty alerts are, alas, common, and we should recognize them.  We would expect developers to ignore any alert that ACR determines to be false. Therefore ACR should be hesitant to determine that an alert may be false, because it is "overriding" the ruling of a SA tool designed to detect true alerts.

### Dependent

This reason means that the alert depends on a previous alert that ACR has already fixed. In the example, ACR might determine lines B and C to be Dependent, and refuse to fix them.

Ideally, a developer could then run their SA tool on the repaired code, and the SA tool would recognize that line A has been fixed. Furthermore, it should also determine that lines B and C no longer require null-pointer checks. Consequently, it would generate no null-pointer alerts over lines A, B, and C.

It is possible that the developer's SA tool is stupid and still generates alerts over lines B and C. If ACR is then run on the code, ACR might determine that lines B and C are False (depending on how much SA effort it does). If ACR has little SA intelligence, it may decide to trust the SA tool and repair line B.
