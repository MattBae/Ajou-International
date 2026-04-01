import React, { useMemo, useState } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

export default function CalendarScreen() {
  const [viewMode, setViewMode] = useState("monthly");
  const [anchorDate, setAnchorDate] = useState(new Date());
  const today = new Date();

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const periodLabel = useMemo(() => {
    if (viewMode === "monthly") {
      return formatMonthlyLabel(anchorDate);
    }
    return formatWeeklyLabel(anchorDate);
  }, [anchorDate, viewMode]);

  const calendarCells = useMemo(() => {
    if (viewMode === "monthly") {
      return buildMonthlyCells(anchorDate);
    }
    return buildWeeklyCells(anchorDate);
  }, [anchorDate, viewMode]);

  const onPressPrev = () => {
    if (viewMode === "monthly") {
      setAnchorDate((prev) => addMonths(prev, -1));
      return;
    }
    setAnchorDate((prev) => addDays(prev, -7));
  };

  const onPressNext = () => {
    if (viewMode === "monthly") {
      setAnchorDate((prev) => addMonths(prev, 1));
      return;
    }
    setAnchorDate((prev) => addDays(prev, 7));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Calendar</Text>

      <View style={styles.topBar}>
        <View style={styles.modeSwitch}>
          <TouchableOpacity
            style={[styles.modeButton, viewMode === "weekly" ? styles.modeButtonActive : null]}
            onPress={() => setViewMode("weekly")}
            activeOpacity={0.85}
          >
            <Text style={[styles.modeButtonText, viewMode === "weekly" ? styles.modeButtonTextActive : null]}>
              Weekly
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeButton, viewMode === "monthly" ? styles.modeButtonActive : null]}
            onPress={() => setViewMode("monthly")}
            activeOpacity={0.85}
          >
            <Text style={[styles.modeButtonText, viewMode === "monthly" ? styles.modeButtonTextActive : null]}>
              Monthly
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.navRow}>
        <TouchableOpacity style={styles.arrowButton} onPress={onPressPrev} activeOpacity={0.85}>
          <Text style={styles.arrowText}>‹</Text>
        </TouchableOpacity>
        <Text style={styles.periodText}>{periodLabel}</Text>
        <TouchableOpacity style={styles.arrowButton} onPress={onPressNext} activeOpacity={0.85}>
          <Text style={styles.arrowText}>›</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.weekHeaderRow}>
        {weekDays.map((day) => (
          <View style={styles.weekHeaderCell} key={day}>
            <Text style={styles.weekHeaderText}>{day}</Text>
          </View>
        ))}
      </View>

      <View style={styles.grid}>
        {calendarCells.map((cell) => (
          <View style={styles.dayCell} key={cell.key}>
            <View
              style={[
                styles.dayBadge,
                !cell.inCurrentPeriod ? styles.dayBadgeMuted : null,
                isSameDay(cell.date, today) ? styles.dayBadgeToday : null,
              ]}
            >
              <Text
                style={[
                  styles.dayText,
                  !cell.inCurrentPeriod ? styles.dayTextMuted : null,
                  isSameDay(cell.date, today) ? styles.dayTextToday : null,
                ]}
              >
                {cell.date.getDate()}
              </Text>
            </View>
          </View>
        ))}
      </View>
    </View>
  );
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function addMonths(date, months) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const day = date.getDate();
  const lastDayOfTargetMonth = new Date(year, month + months + 1, 0).getDate();
  const target = new Date(year, month + months, Math.min(day, lastDayOfTargetMonth));
  return target;
}

function formatMonthlyLabel(date) {
  return `${date.getFullYear()}년 ${date.getMonth() + 1}월`;
}

function startOfWeekMonday(date) {
  const base = new Date(date);
  const weekday = base.getDay(); // Sun:0, Mon:1, ... Sat:6
  const diffToMonday = weekday === 0 ? -6 : 1 - weekday;
  base.setDate(base.getDate() + diffToMonday);
  return base;
}

function formatWeeklyLabel(date) {
  const weekStart = startOfWeekMonday(date);
  const weekEnd = addDays(weekStart, 6);
  return `${weekStart.getFullYear()}.${weekStart.getMonth() + 1}.${weekStart.getDate()} - ${weekEnd.getFullYear()}.${
    weekEnd.getMonth() + 1
  }.${weekEnd.getDate()}`;
}

function buildMonthlyCells(anchorDate) {
  const year = anchorDate.getFullYear();
  const month = anchorDate.getMonth();
  const firstOfMonth = new Date(year, month, 1);
  const lastOfMonth = new Date(year, month + 1, 0);

  const firstWeekday = firstOfMonth.getDay(); // Sun:0 ... Sat:6
  const leadingCount = firstWeekday === 0 ? 6 : firstWeekday - 1; // Mon-based
  const daysInMonth = lastOfMonth.getDate();

  const cells = [];
  for (let i = 0; i < leadingCount; i += 1) {
    const date = addDays(firstOfMonth, -(leadingCount - i));
    cells.push({
      key: `prev-${date.toISOString()}`,
      date,
      inCurrentPeriod: false,
    });
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day);
    cells.push({
      key: `curr-${date.toISOString()}`,
      date,
      inCurrentPeriod: true,
    });
  }

  const trailingCount = (7 - (cells.length % 7)) % 7;
  const lastDate = new Date(year, month, daysInMonth);
  for (let i = 1; i <= trailingCount; i += 1) {
    const date = addDays(lastDate, i);
    cells.push({
      key: `next-${date.toISOString()}`,
      date,
      inCurrentPeriod: false,
    });
  }

  return cells;
}

function buildWeeklyCells(anchorDate) {
  const weekStart = startOfWeekMonday(anchorDate);
  const cells = [];
  for (let i = 0; i < 7; i += 1) {
    const date = addDays(weekStart, i);
    cells.push({
      key: `week-${date.toISOString()}`,
      date,
      inCurrentPeriod: true,
    });
  }
  return cells;
}

function isSameDay(a, b) {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#ffffff",
    paddingTop: 18,
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 30,
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: 12,
  },
  topBar: {
    marginBottom: 12,
  },
  modeSwitch: {
    flexDirection: "row",
    backgroundColor: "#f1f5f9",
    borderRadius: 10,
    padding: 4,
    gap: 6,
  },
  modeButton: {
    flex: 1,
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 8,
  },
  modeButtonActive: {
    backgroundColor: "#2f6df6",
  },
  modeButtonText: {
    color: "#334155",
    fontSize: 14,
    fontWeight: "700",
  },
  modeButtonTextActive: {
    color: "#ffffff",
  },
  navRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 14,
  },
  arrowButton: {
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: "#dbe4f3",
    backgroundColor: "#f8fafc",
  },
  arrowText: {
    fontSize: 22,
    lineHeight: 24,
    color: "#334155",
  },
  periodText: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0f172a",
  },
  weekHeaderRow: {
    flexDirection: "row",
    marginBottom: 8,
  },
  weekHeaderCell: {
    flex: 1,
    alignItems: "center",
  },
  weekHeaderText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#64748b",
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 12,
    overflow: "hidden",
    backgroundColor: "#ffffff",
  },
  dayCell: {
    width: "14.2857%",
    minHeight: 58,
    borderRightWidth: 1,
    borderBottomWidth: 1,
    borderRightColor: "#f1f5f9",
    borderBottomColor: "#f1f5f9",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 8,
  },
  dayBadge: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
  },
  dayBadgeMuted: {
    backgroundColor: "#f8fafc",
  },
  dayBadgeToday: {
    backgroundColor: "#E85D75",
  },
  dayText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#1e293b",
  },
  dayTextMuted: {
    color: "#94a3b8",
  },
  dayTextToday: {
    color: "#ffffff",
    fontWeight: "700",
  },
});
