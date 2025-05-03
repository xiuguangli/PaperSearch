<?php
// 设置响应头
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// 获取当前目录下的所有JSON文件
$files = glob(__DIR__ . '/*.json');
$datasets = [];

// 解析文件名，提取会议和年份信息
foreach ($files as $file) {
    $filename = basename($file);
    if (preg_match('/^([A-Za-z]+)\.(\d{4})\.json$/', $filename, $matches)) {
        $conference = $matches[1];
        $year = $matches[2];
        $datasets[] = [
            'conference' => $conference,
            'year' => $year,
            'filename' => $filename
        ];
    }
}

// 返回JSON格式的数据
echo json_encode(['datasets' => $datasets], JSON_PRETTY_PRINT);
