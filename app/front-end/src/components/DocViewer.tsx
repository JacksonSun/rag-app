import * as React from "react";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import { ResultSource } from "@/app/api/models";
import { Anchor } from "@mui/icons-material";
import DocViewer, { DocViewerRenderers } from "@cyntler/react-doc-viewer";
import path from "path";
import url from "url";
import Button from "@mui/material/Button";

type Anchor = "top" | "left" | "bottom" | "right";

const getFileFormatFromUrl = (url: string) => {
  const parts = url.split(".");
  if (parts.length > 1) {
    return parts[parts.length - 1];
  }
  return "Unknown";
};

const extractFileNameFromUrl = (inputUrl: string) => {
  const parsedUrl = url.parse(inputUrl);
  const pathname = parsedUrl.pathname;

  if (!pathname) {
    throw new Error("Invalid URL");
  }

  const decodedPathname = decodeURIComponent(pathname);
  const fileName = path.basename(decodedPathname);
  return fileName;
};

export default function TemporaryDrawer({ source }: { source: ResultSource }) {
  const docs = [
    {
      uri: source.metadata.url,
      fileType: getFileFormatFromUrl(source.metadata.url),
      fileName: source.metadata.title,
    },
  ];

  const [state, setState] = React.useState({
    top: false,
    left: false,
    bottom: false,
    right: false,
  });

  const toggleDrawer =
    (anchor: Anchor, open: boolean) =>
    (event: React.KeyboardEvent | React.MouseEvent) => {
      if (
        event.type === "keydown" &&
        ((event as React.KeyboardEvent).key === "Tab" ||
          (event as React.KeyboardEvent).key === "Shift")
      ) {
        return;
      }

      setState({ ...state, [anchor]: open });
    };

  const list = (anchor: Anchor) => (
    <Box
      sx={{ width: anchor === "top" || anchor === "bottom" ? "auto" : 800 }}
      role="presentation"
      //onClick={toggleDrawer(anchor, false)}
      //onKeyDown={toggleDrawer(anchor, false)}
    >
      <DocViewer
        documents={docs}
        pluginRenderers={DocViewerRenderers}
        config={{
          pdfVerticalScrollByDefault: true,
        }}
      />
    </Box>
  );

  return (
    <div>
      <React.Fragment key={"right"}>
        <Button
          variant="text"
          onClick={toggleDrawer("right", true)}
          sx={{
            textDecoration: "underline",
            fontSize: "1 rem",
            fontWeight: 500,
          }}
        >
          {source.metadata.title}
        </Button>
        <Drawer
          anchor={"right"}
          open={state["right"]}
          onClose={toggleDrawer("right", false)}
        >
          {list("right")}
        </Drawer>
      </React.Fragment>
    </div>
  );
}
