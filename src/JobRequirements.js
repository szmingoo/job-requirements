import React, { useState, useRef } from 'react';
import './JobRequirements.css';
import axios from 'axios';

const uploadResume = (file) => {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);

        axios.post('http://127.0.0.1:8073/api/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
            .then((response) => {
                console.log('File uploaded successfully:', response.data);
                resolve('上传成功');
            })
            .catch((error) => {
                console.error('Error uploading file:', error);
                reject('上传失败');
            });
    });
};

const JobRequirements = () => {
    const [position, setPosition] = useState('');
    const [htmlContent, setHtmlContent] = useState('');

    const handlePositionChange = (event) => {
        setPosition(event.target.value);
    };

    const fileInputRef = useRef(null);

    const handleFileChange = async (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            try {
                const result = await uploadResume(selectedFile);
                alert(result);
                fileInputRef.current.value = null;
            } catch (error) {
                alert(error);
                fileInputRef.current.value = null;
            }
        }
    };

    const handleMatch = async () => {
        alert("简历正在解析中，请稍后查看报告...");
        try {
            const response = await axios.post('http://127.0.0.1:8073/api/report', {
                position: position
            });
            const res = response.data;
            alert("简历解析成功");
            setHtmlContent(res.htmlContent);
        } catch (error) {
            console.error('Error generating report:', error);
            alert('生成报告失败');
        }
    };

    const handleViewReport = () => {
        const newWindow = window.open('', 'report');
        newWindow.document.write('<html><head><title>报告</title></head><body>' + htmlContent + '</body></html>');
        newWindow.document.close();
    };

    const handleClearData = () => {
        setPosition(''); // Reset position state
        setHtmlContent(''); // Reset htmlContent state
    };

    return (
        <div className="job-requirements">
            <h1>简历筛选</h1>
            <textarea
                value={position}
                onChange={handlePositionChange}
                rows={20}
                className="position-requirements-textarea"
                placeholder={`任职要求：
1、有1年以上调解经验，或催收、法催经验【50】； 
2、大专以上学历，法律、法学或金融相关专业优先【10】；
3、有法律行业、法院行业、互联网行业、金融行业工作经验者优先【15】；
4、具备较强的沟通能力、有耐心【15】；
5、熟练操作电脑【5】；
6、性格开朗，有较强的团队意识、抗压能力、逻辑能力、沟通协作能力【5】；
7、没有做过反催收【必须项】

注释：【】中文括号里填写的是匹配权重，如：【10%】表示该条件匹配的权重为10%，总计为100%`}
            />
            <input
                type="file"
                onChange={handleFileChange}
                ref={fileInputRef}
                style={{ display: 'none' }}
            />
            <div className="buttons">
                <div className="button-row">
                    <button onClick={() => fileInputRef.current.click()}>上传文件</button>
                    <button onClick={handleMatch}>开始匹配</button>
                </div>
                <div className="button-row">
                    <button onClick={handleViewReport}>查看报告</button>
                    <button onClick={handleClearData}>清空数据</button>
                </div>
            </div>
        </div>
    );
};

export default JobRequirements;








// npm install -g create-react-app
// npx create-react-app resume-screening
// npm install react-router-dom
// npm start

// npm install
// npm run build(或npx react-scripts build)


// sudo apt-get install ufw
// sudo ufw enable
// sudo ufw allow 3000/tcp
// sudo ufw status



// sudo chown -R www-data:www-data /root/resume-screening/build/
// sudo chmod -R 755 /path/to/your/react/app/build
