// Web Worker for loading and processing paper data
self.onmessage = async function(e) {
  const { url, batchSize = 100 } = e.data;
  
  try {
    // 发送开始加载的消息
    self.postMessage({ type: 'loading-start' });
    
    // 获取数据
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    // 解析JSON
    const data = await response.json();
    
    if (!data || !Array.isArray(data.papers)) {
      throw new Error('Invalid data format');
    }
    
    const papers = data.papers;
    const totalPapers = papers.length;
    
    // 发送元数据信息
    self.postMessage({
      type: 'metadata',
      totalPapers,
      totalBatches: Math.ceil(totalPapers / batchSize)
    });
    
    // 分批处理数据
    for (let i = 0; i < totalPapers; i += batchSize) {
      const batch = papers.slice(i, i + batchSize);
      
      // 发送批次数据
      self.postMessage({
        type: 'batch',
        batch,
        batchIndex: Math.floor(i / batchSize),
        startIndex: i,
        endIndex: Math.min(i + batchSize, totalPapers)
      });
      
      // 给UI线程一些时间来处理
      await new Promise(resolve => setTimeout(resolve, 10));
    }
    
    // 发送完成消息
    self.postMessage({
      type: 'complete',
      totalPapers,
      paperData: data
    });
    
  } catch (error) {
    // 发送错误消息
    self.postMessage({
      type: 'error',
      error: error.message
    });
  }
};
