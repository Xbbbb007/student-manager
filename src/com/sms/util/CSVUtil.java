package com.sms.util;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

public class CSVUtil {

    public static List<List<String>> readCSV(String filePath) throws Exception {
        List<List<String>> data = new ArrayList<>();
        File file = new File(filePath);
        if (!file.exists()) {
            return data;
        }

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    continue;
                }
                // Handle basic comma separation and quoted commas
                List<String> row = parseCSVLine(line);
                data.add(row);
            }
        }
        return data;
    }

    public static void writeCSV(String filePath, List<String> headers, List<List<String>> rows) throws Exception {
        File file = new File(filePath);
        File parent = file.getParentFile();
        if (parent != null && !parent.exists()) {
            parent.mkdirs();
        }

        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8))) {
            // Write BOM for Excel compatibility with UTF-8
            writer.write('\ufeff');

            // Write headers
            if (headers != null && !headers.isEmpty()) {
                writer.write(joinCSVRow(headers));
                writer.newLine();
            }

            // Write rows
            for (List<String> row : rows) {
                writer.write(joinCSVRow(row));
                writer.newLine();
            }
        }
    }

    private static List<String> parseCSVLine(String line) {
        List<String> row = new ArrayList<>();
        StringBuilder cell = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                row.add(cell.toString().trim());
                cell.setLength(0);
            } else {
                cell.append(c);
            }
        }
        row.add(cell.toString().trim());
        return row;
    }

    private static String joinCSVRow(List<String> row) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < row.size(); i++) {
            String val = row.get(i);
            if (val == null) {
                val = "";
            }
            if (val.contains(",") || val.contains("\"") || val.contains("\n")) {
                val = "\"" + val.replace("\"", "\"\"") + "\"";
            }
            sb.append(val);
            if (i < row.size() - 1) {
                sb.append(",");
            }
        }
        return sb.toString();
    }
}
