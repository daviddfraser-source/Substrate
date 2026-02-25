(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/app/gantt/page.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>GanttPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
(()=>{
    const e = new Error("Cannot find module 'gantt-task-react/dist/index.css'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$shared$2f$lib$2f$app$2d$dynamic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/shared/lib/app-dynamic.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$alert$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Alert$3e$__ = __turbopack_context__.i("[project]/node_modules/antd/es/alert/index.js [app-client] (ecmascript) <export default as Alert>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$card$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Card$3e$__ = __turbopack_context__.i("[project]/node_modules/antd/es/card/index.js [app-client] (ecmascript) <export default as Card>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$segmented$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Segmented$3e$__ = __turbopack_context__.i("[project]/node_modules/antd/es/segmented/index.js [app-client] (ecmascript) <export default as Segmented>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$space$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__$3c$export__default__as__Space$3e$__ = __turbopack_context__.i("[project]/node_modules/antd/es/space/index.js [app-client] (ecmascript) <locals> <export default as Space>");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$typography$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Typography$3e$__ = __turbopack_context__.i("[project]/node_modules/antd/es/typography/index.js [app-client] (ecmascript) <export default as Typography>");
(()=>{
    const e = new Error("Cannot find module 'gantt-task-react'");
    e.code = 'MODULE_NOT_FOUND';
    throw e;
})();
;
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
const GanttChart = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$shared$2f$lib$2f$app$2d$dynamic$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"])(()=>(()=>{
        const e = new Error("Cannot find module 'gantt-task-react'");
        e.code = 'MODULE_NOT_FOUND';
        throw e;
    })().then((mod)=>mod.Gantt), {
    loadableGenerated: {
        modules: [
            null
        ]
    },
    ssr: false
});
_c = GanttChart;
const seedTasks = [
    {
        id: "G-01",
        name: "Discovery and architecture",
        start: new Date(2026, 1, 24),
        end: new Date(2026, 1, 27),
        type: "task",
        progress: 90,
        isDisabled: false,
        styles: {
            progressColor: "#1677ff",
            progressSelectedColor: "#0958d9"
        }
    },
    {
        id: "G-02",
        name: "Template library integration",
        start: new Date(2026, 1, 27),
        end: new Date(2026, 2, 3),
        type: "task",
        progress: 45,
        dependencies: [
            "G-01"
        ],
        isDisabled: false,
        styles: {
            progressColor: "#13c2c2",
            progressSelectedColor: "#08979c"
        }
    },
    {
        id: "G-03",
        name: "Playwright and QA hardening",
        start: new Date(2026, 2, 3),
        end: new Date(2026, 2, 6),
        type: "task",
        progress: 20,
        dependencies: [
            "G-02"
        ],
        isDisabled: false,
        styles: {
            progressColor: "#fa8c16",
            progressSelectedColor: "#d46b08"
        }
    },
    {
        id: "G-04",
        name: "Release candidate",
        start: new Date(2026, 2, 6),
        end: new Date(2026, 2, 7),
        type: "milestone",
        progress: 0,
        dependencies: [
            "G-03"
        ],
        isDisabled: false,
        styles: {
            progressColor: "#722ed1",
            progressSelectedColor: "#531dab"
        }
    }
];
const VIEW_OPTIONS = [
    {
        label: "Day",
        value: ViewMode.Day
    },
    {
        label: "Week",
        value: ViewMode.Week
    },
    {
        label: "Month",
        value: ViewMode.Month
    }
];
function GanttPage() {
    _s();
    const [tasks, setTasks] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(seedTasks);
    const [viewMode, setViewMode] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(ViewMode.Week);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "p-6 space-y-4",
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$space$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__$3c$export__default__as__Space$3e$__["Space"], {
                orientation: "vertical",
                size: 4,
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$typography$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Typography$3e$__["Typography"].Title, {
                        level: 2,
                        className: "!mb-0",
                        children: "Gantt Template"
                    }, void 0, false, {
                        fileName: "[project]/app/gantt/page.tsx",
                        lineNumber: 72,
                        columnNumber: 9
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$typography$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Typography$3e$__["Typography"].Text, {
                        type: "secondary",
                        children: "Powered by `gantt-task-react` with drag-to-reschedule and progress editing."
                    }, void 0, false, {
                        fileName: "[project]/app/gantt/page.tsx",
                        lineNumber: 73,
                        columnNumber: 9
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/app/gantt/page.tsx",
                lineNumber: 71,
                columnNumber: 7
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$card$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Card$3e$__["Card"], {
                children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$space$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$locals$3e$__$3c$export__default__as__Space$3e$__["Space"], {
                    orientation: "vertical",
                    className: "w-full",
                    size: 16,
                    children: [
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$segmented$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Segmented$3e$__["Segmented"], {
                            value: viewMode,
                            options: VIEW_OPTIONS.map((option)=>({
                                    label: option.label,
                                    value: option.value
                                })),
                            onChange: (value)=>setViewMode(value)
                        }, void 0, false, {
                            fileName: "[project]/app/gantt/page.tsx",
                            lineNumber: 80,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$antd$2f$es$2f$alert$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__$3c$export__default__as__Alert$3e$__["Alert"], {
                            showIcon: true,
                            type: "info",
                            title: "Interactive Gantt",
                            description: "Drag a bar edge to change dates or drag progress to update completion."
                        }, void 0, false, {
                            fileName: "[project]/app/gantt/page.tsx",
                            lineNumber: 85,
                            columnNumber: 11
                        }, this),
                        /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "overflow-auto border border-token-border-default rounded-md bg-white",
                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(GanttChart, {
                                tasks: tasks,
                                viewMode: viewMode,
                                listCellWidth: "210px",
                                columnWidth: viewMode === ViewMode.Day ? 60 : 90,
                                onDateChange: (task)=>{
                                    setTasks((prev)=>prev.map((existing)=>existing.id === task.id ? task : existing));
                                    return true;
                                },
                                onProgressChange: (task)=>{
                                    setTasks((prev)=>prev.map((existing)=>existing.id === task.id ? task : existing));
                                    return true;
                                },
                                onDelete: (task)=>{
                                    setTasks((prev)=>prev.filter((existing)=>existing.id !== task.id));
                                    return true;
                                }
                            }, void 0, false, {
                                fileName: "[project]/app/gantt/page.tsx",
                                lineNumber: 92,
                                columnNumber: 13
                            }, this)
                        }, void 0, false, {
                            fileName: "[project]/app/gantt/page.tsx",
                            lineNumber: 91,
                            columnNumber: 11
                        }, this)
                    ]
                }, void 0, true, {
                    fileName: "[project]/app/gantt/page.tsx",
                    lineNumber: 79,
                    columnNumber: 9
                }, this)
            }, void 0, false, {
                fileName: "[project]/app/gantt/page.tsx",
                lineNumber: 78,
                columnNumber: 7
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/app/gantt/page.tsx",
        lineNumber: 70,
        columnNumber: 5
    }, this);
}
_s(GanttPage, "eui3Y/H4bCH+6bkODwU/5CCkBSw=");
_c1 = GanttPage;
var _c, _c1;
__turbopack_context__.k.register(_c, "GanttChart");
__turbopack_context__.k.register(_c1, "GanttPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=app_gantt_page_tsx_5fe9dc97._.js.map