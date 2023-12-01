; ModuleID = 'simple_null_check.c'
source_filename = "simple_null_check.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [21 x i8] c"Error: null pointer!\00", align 1, !dbg !0

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @foo(ptr noundef %0) #0 !dbg !17 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !23, metadata !DIExpression()), !dbg !24
  %3 = load ptr, ptr %2, align 8, !dbg !25
  %4 = icmp ne ptr %3, null, !dbg !25
  br i1 %4, label %7, label %5, !dbg !27

5:                                                ; preds = %1
  %6 = call i32 @puts(ptr noundef @.str), !dbg !28
  br label %7, !dbg !30

7:                                                ; preds = %5, %1
  %8 = load ptr, ptr %2, align 8, !dbg !31
  %9 = load i32, ptr %8, align 4, !dbg !32
  ret i32 %9, !dbg !33
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

declare i32 @puts(ptr noundef) #2

attributes #0 = { noinline nounwind uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!7}
!llvm.module.flags = !{!9, !10, !11, !12, !13, !14, !15}
!llvm.ident = !{!16}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(scope: null, file: !2, line: 5, type: !3, isLocal: true, isDefinition: true)
!2 = !DIFile(filename: "simple_null_check.c", directory: "/host/code/acr/test", checksumkind: CSK_MD5, checksum: "2982177e92f5bee3234c7651eed6551e")
!3 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 168, elements: !5)
!4 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!5 = !{!6}
!6 = !DISubrange(count: 21)
!7 = distinct !DICompileUnit(language: DW_LANG_C99, file: !2, producer: "Ubuntu clang version 15.0.7", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !8, splitDebugInlining: false, nameTableKind: None)
!8 = !{!0}
!9 = !{i32 7, !"Dwarf Version", i32 5}
!10 = !{i32 2, !"Debug Info Version", i32 3}
!11 = !{i32 1, !"wchar_size", i32 4}
!12 = !{i32 7, !"PIC Level", i32 2}
!13 = !{i32 7, !"PIE Level", i32 2}
!14 = !{i32 7, !"uwtable", i32 2}
!15 = !{i32 7, !"frame-pointer", i32 2}
!16 = !{!"Ubuntu clang version 15.0.7"}
!17 = distinct !DISubprogram(name: "foo", scope: !2, file: !2, line: 3, type: !18, scopeLine: 3, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !7, retainedNodes: !22)
!18 = !DISubroutineType(types: !19)
!19 = !{!20, !21}
!20 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!21 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !20, size: 64)
!22 = !{}
!23 = !DILocalVariable(name: "p", arg: 1, scope: !17, file: !2, line: 3, type: !21)
!24 = !DILocation(line: 3, column: 14, scope: !17)
!25 = !DILocation(line: 4, column: 10, scope: !26)
!26 = distinct !DILexicalBlock(scope: !17, file: !2, line: 4, column: 9)
!27 = !DILocation(line: 4, column: 9, scope: !17)
!28 = !DILocation(line: 5, column: 9, scope: !29)
!29 = distinct !DILexicalBlock(scope: !26, file: !2, line: 4, column: 13)
!30 = !DILocation(line: 7, column: 5, scope: !29)
!31 = !DILocation(line: 8, column: 13, scope: !17)
!32 = !DILocation(line: 8, column: 12, scope: !17)
!33 = !DILocation(line: 8, column: 5, scope: !17)
