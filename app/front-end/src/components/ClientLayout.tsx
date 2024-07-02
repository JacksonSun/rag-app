"use client";

import * as React from "react";
import Box from "@mui/material/Box";
import SearchIcon from "@mui/icons-material/Search";
import FolderIcon from "@mui/icons-material/Folder";
import ThemeRegistry from "@/components/ThemeRegistry/ThemeRegistry";
import { styled, useTheme } from "@mui/material/styles";
import SideMenu from "./SideMenu";
import Grid from "@mui/material/Grid";

const menuItems = [
  { label: "Home", href: "/", icon: SearchIcon },
  { label: "File Management", href: "/file_management", icon: FolderIcon },
];

const drawerWidth = 240;

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create("margin", {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: `-${drawerWidth}px`,
  ...(open && {
    transition: theme.transitions.create("margin", {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginLeft: 0,
  }),
}));

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [open, setOpen] = React.useState(true);

  return (
    <html lang="en" style={{ height: "100%" }}>
      <body style={{ height: "100%", margin: 0 }}>
        <Box sx={{ display: "flex", height: "100%" }}>
          <ThemeRegistry>
            <Grid container direction="row">
              <Grid item xs={2} sx={{ borderRight: "1px solid #E6E6E6" }}>
                <SideMenu items={menuItems} />
              </Grid>
              <Grid item xs={10} sx={{ mt: 4 }}>
                <Main open={open} sx={{ padding: "0px" }}>
                  {children}
                </Main>
              </Grid>
            </Grid>
          </ThemeRegistry>
        </Box>
      </body>
    </html>
  );
}
