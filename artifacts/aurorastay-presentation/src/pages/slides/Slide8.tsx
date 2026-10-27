import React, { useState, useEffect, useRef } from "react";
import img_1 from "./assets/images/image_1.png";
const Slide8: React.FC = () => {
  const outerRef = useRef<HTMLDivElement>(null);
  const [layout, setLayout] = useState({
    s: 1,
    x: 0,
    y: 0
  });
  useEffect(() => {
    const el = outerRef.current;
    if (!el) return;
    const update = () => {
      const w = el.clientWidth;
      const h = el.clientHeight;
      const s = Math.min(w / 960, h / 540);
      setLayout({
        s,
        x: (w - 960 * s) / 2,
        y: (h - 540 * s) / 2
      });
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return <div id="slide-8" ref={outerRef} className="w-screen h-screen overflow-hidden relative" style={{
    backgroundColor: "#000"
  }}><div id="slide-inner-8" style={{
      position: "absolute",
      width: "960px",
      height: "540px",
      overflow: "hidden",
      transformOrigin: "top left",
      color: "#000000",
      backgroundColor: "#ffffff",
      transform: `scale(${layout.s})`,
      left: layout.x + "px",
      top: layout.y + "px"
    }}><div key={0} style={{
        position: "absolute",
        left: "234.58px",
        top: "516.29px",
        width: "490.83px",
        height: "28.94px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "center",
          lineHeight: "1.23",
          paddingLeft: "1.33px",
          fontSize: "calc(7pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(7pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            fontWeight: "700",
            color: "#434343"
          }}>{"Proprietary content. \xA9 Great Learning. All Rights Reserved. Unauthorized use or distribution prohibited."}</span></p></div><img key={1} src={img_1} alt="Google Shape;10;p1" style={{
        position: "absolute",
        left: "805.2px",
        top: "7.17px",
        width: "146.51px",
        height: "60.13px",
        boxSizing: "border-box",
        objectFit: "fill"
      }} /><div key={2} style={{
        position: "absolute",
        left: "0.69px",
        top: "0px",
        width: "18.43px",
        height: "74.46px"
      }}><div key={0} style={{
          position: "absolute",
          left: "0px",
          top: "0px",
          width: "18.43px",
          height: "37.32px",
          boxSizing: "border-box",
          backgroundColor: "#0E39A9"
        }} /><div key={1} style={{
          position: "absolute",
          left: "0px",
          top: "37.14px",
          width: "18.43px",
          height: "37.32px",
          boxSizing: "border-box",
          backgroundColor: "#1974D2"
        }} /></div><div key={3} style={{
        position: "absolute",
        left: "21.27px",
        top: "30.37px",
        width: "894.55px",
        height: "60.13px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "left",
          lineHeight: "1.2",
          fontSize: "calc(24pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(24pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            fontWeight: "700",
            color: "#0E39A9"
          }}>{"Policy Chunk Example"}</span></p></div><div key={4} style={{
        position: "absolute",
        left: "42.35px",
        top: "148.44px",
        width: "20.28px",
        height: "20.28px",
        boxSizing: "border-box",
        backgroundColor: "#0944A1",
        border: "1px solid #FFFFFF"
      }} /><div key={5} style={{
        position: "absolute",
        left: "72.63px",
        top: "137.03px",
        width: "851.18px",
        height: "68.03px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "left",
          lineHeight: "1.38",
          fontSize: "calc(14pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(14pt * var(--pptx-font-scale, 1))",
            fontFamily: "Montserrat, 'Helvetica Neue', Arial, sans-serif"
          }}>{"61 chunks from 19 pages. Example: “ASH-CHI Loop lists a $50 per night pet fee, capped at $150 per stay.” Citation metadata is retained as source filename and page."}</span></p></div><div key={6} style={{
        position: "absolute",
        left: "34.15px",
        top: "460.88px",
        width: "881.67px",
        height: "45.26px",
        boxSizing: "border-box",
        backgroundColor: "transparent",
        padding: "9.6px 9.6px 9.6px 9.6px",
        wordWrap: "break-word"
      }}><p style={{
          textAlign: "left",
          lineHeight: "1.38",
          fontSize: "calc(16pt * var(--pptx-font-scale, 1))",
          marginTop: "0",
          marginBottom: "0"
        }}><span style={{
            fontSize: "calc(16pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            fontWeight: "700",
            color: "#000000"
          }}>{""}</span><span style={{
            fontSize: "calc(16pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            color: "#000000"
          }}>{""}</span><span style={{
            fontStyle: "italic",
            fontSize: "calc(16pt * var(--pptx-font-scale, 1))",
            fontFamily: "'Nunito', sans-serif",
            color: "#000000"
          }}>{""}</span></p></div></div></div>;
};
export default Slide8;
