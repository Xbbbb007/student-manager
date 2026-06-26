package com.sms.util;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class ConsoleUtil {

    private static final Scanner scanner = new Scanner(System.in);
    private static final SimpleDateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");

    static {
        DATE_FORMAT.setLenient(false);
    }

    public static void printHeader(String title) {
        System.out.println("==================================================");
        System.out.println("  " + title);
        System.out.println("==================================================");
    }

    public static void printMenu(String title, List<String> items) {
        printHeader(title);
        for (String item : items) {
            System.out.println("  " + item);
        }
        System.out.println("--------------------------------------------------");
    }

    public static String readLine(String prompt) {
        System.out.print(prompt + " > ");
        return scanner.nextLine().trim();
    }

    public static String readLine(String prompt, boolean allowEmpty) {
        while (true) {
            String input = readLine(prompt);
            if (!allowEmpty && input.isEmpty()) {
                printError("输入不能为空，请重新输入");
                continue;
            }
            return input;
        }
    }

    public static int readChoice(String prompt, int max) {
        return readInt(prompt, 0, max);
    }

    public static int readInt(String prompt, int min, int max) {
        while (true) {
            String input = readLine(prompt);
            try {
                int value = Integer.parseInt(input);
                if (value < min || value > max) {
                    printError(String.format("输入超出范围 [%d-%d]，请重新输入", min, max));
                    continue;
                }
                return value;
            } catch (NumberFormatException e) {
                printError("请输入有效的整数");
            }
        }
    }

    public static double readDouble(String prompt, double min, double max) {
        while (true) {
            String input = readLine(prompt);
            try {
                double value = Double.parseDouble(input);
                if (value < min || value > max) {
                    printError(String.format("输入超出范围 [%.2f-%.2f]，请重新输入", min, max));
                    continue;
                }
                return value;
            } catch (NumberFormatException e) {
                printError("请输入有效的数字");
            }
        }
    }

    public static boolean confirm(String message) {
        while (true) {
            String input = readLine(message + " (y/n)");
            if (input.equalsIgnoreCase("y") || input.equalsIgnoreCase("yes")) {
                return true;
            } else if (input.equalsIgnoreCase("n") || input.equalsIgnoreCase("no")) {
                return false;
            } else {
                printError("请输入 y 或 n");
            }
        }
    }

    public static java.sql.Date readDate(String prompt) {
        while (true) {
            String input = readLine(prompt + " (格式: yyyy-MM-dd)");
            if (input.isEmpty()) {
                printError("日期不能为空");
                continue;
            }
            try {
                java.util.Date parsed = DATE_FORMAT.parse(input);
                return new java.sql.Date(parsed.getTime());
            } catch (ParseException e) {
                printError("日期格式不正确，请使用 yyyy-MM-dd");
            }
        }
    }

    public static java.sql.Date readDateOptional(String prompt, java.sql.Date defaultDate) {
        while (true) {
            String promptStr = defaultDate != null ? 
                String.format("%s (回车默认: %s, 格式: yyyy-MM-dd)", prompt, DATE_FORMAT.format(defaultDate)) :
                prompt + " (回车跳过, 格式: yyyy-MM-dd)";
            String input = readLine(promptStr);
            if (input.isEmpty()) {
                return defaultDate;
            }
            try {
                java.util.Date parsed = DATE_FORMAT.parse(input);
                return new java.sql.Date(parsed.getTime());
            } catch (ParseException e) {
                printError("日期格式不正确，请使用 yyyy-MM-dd");
            }
        }
    }

    public static void clearScreen() {
        // Output newlines to push older text up, works across all console types
        for (int i = 0; i < 30; i++) {
            System.out.println();
        }
    }

    public static void printSuccess(String msg) {
        System.out.println("[成功] " + msg);
    }

    public static void printError(String msg) {
        System.out.println("[错误] " + msg);
    }

    public static void pause() {
        System.out.print("按回车键继续...");
        scanner.nextLine();
    }

    // Chinese-aware table formatting
    public static void printTable(List<String> headers, List<List<String>> rows) {
        if (headers == null || headers.isEmpty()) return;

        // Calculate column widths
        int[] widths = new int[headers.size()];
        for (int i = 0; i < headers.size(); i++) {
            widths[i] = getDisplayWidth(headers.get(i));
        }

        for (List<String> row : rows) {
            for (int i = 0; i < Math.min(row.size(), widths.length); i++) {
                widths[i] = Math.max(widths[i], getDisplayWidth(row.get(i)));
            }
        }

        // Print header line
        StringBuilder sbHeader = new StringBuilder();
        StringBuilder sbSeparator = new StringBuilder();
        for (int i = 0; i < headers.size(); i++) {
            sbHeader.append(padRight(headers.get(i), widths[i]));
            sbSeparator.append("-".repeat(widths[i]));
            if (i < headers.size() - 1) {
                sbHeader.append(" | ");
                sbSeparator.append("-+-");
            }
        }
        System.out.println(sbHeader.toString());
        System.out.println(sbSeparator.toString());

        // Print data rows
        for (List<String> row : rows) {
            StringBuilder sbRow = new StringBuilder();
            for (int i = 0; i < headers.size(); i++) {
                String val = i < row.size() ? row.get(i) : "";
                sbRow.append(padRight(val, widths[i]));
                if (i < headers.size() - 1) {
                    sbRow.append(" | ");
                }
            }
            System.out.println(sbRow.toString());
        }
    }

    public static int getDisplayWidth(String s) {
        if (s == null) return 0;
        int width = 0;
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (isChinese(c)) {
                width += 2;
            } else {
                width += 1;
            }
        }
        return width;
    }

    public static String padRight(String s, int width) {
        if (s == null) s = "";
        int displayWidth = getDisplayWidth(s);
        int padCount = width - displayWidth;
        if (padCount <= 0) return s;
        return s + " ".repeat(padCount);
    }

    private static boolean isChinese(char c) {
        Character.UnicodeBlock ub = Character.UnicodeBlock.of(c);
        return ub == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS
                || ub == Character.UnicodeBlock.CJK_COMPATIBILITY_IDEOGRAPHS
                || ub == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_A
                || ub == Character.UnicodeBlock.CJK_UNIFIED_IDEOGRAPHS_EXTENSION_B
                || ub == Character.UnicodeBlock.CJK_SYMBOLS_AND_PUNCTUATION
                || ub == Character.UnicodeBlock.HALFWIDTH_AND_FULLWIDTH_FORMS
                || ub == Character.UnicodeBlock.GENERAL_PUNCTUATION;
    }

    // Text bar charts
    public static void printBarChart(String title, List<String> labels, List<Integer> values, List<Double> percentages) {
        System.out.println("---- " + title + " ----");
        int total = 0;
        for (int val : values) {
            total += val;
        }

        for (int i = 0; i < labels.size(); i++) {
            String label = labels.get(i);
            int val = values.get(i);
            double pct = percentages.get(i);
            // Draw progress bar block
            int blocks = (int) Math.round(pct / 5.0); // 1 block per 5%
            String bar = "█".repeat(blocks);
            System.out.printf("  %s: %s %d人 (%.1f%%)\n", padRight(label, 10), bar, val, pct);
        }
        System.out.println("--------------------------------------------------");
    }
}
