import React, { useEffect, useState } from 'react';

const ReportPage = () => {
    const [htmlContent, setHtmlContent] = useState('');

    useEffect(() => {
        // 从 localStorage 中获取 HTML 内容
        const storedHtmlContent = localStorage.getItem('htmlContent');
        setHtmlContent(storedHtmlContent);
    }, []);

    return (
        <div className="report-page" dangerouslySetInnerHTML={{ __html: htmlContent }} />
    );
};

export default ReportPage;
