import { Roboto } from "next/font/google";
import { createTheme } from "@mui/material/styles";

const roboto = Roboto({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  display: "swap",
});

const brandColors = {
  // default: "#00ACBB",
  default: "#051C2C",
  deep_blue: "#051C2C",
  white: "#FFFFFF",
  electric_blue: "#2251FF",
  cyan: "#00A9F4",
  black: "#000000",
  grey: "#E6E6E6",
};

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: brandColors.deep_blue,
      contrastText: "#fff", // white
    },
    secondary: {
      main: brandColors.electric_blue,
      contrastText: "#fff", // white
    },
  },
  typography: {
    fontFamily: roboto.style.fontFamily,
  },
  components: {
    MuiAlert: {
      styleOverrides: {
        root: ({ ownerState }) => ({
          ...(ownerState.severity === "info" && {
            backgroundColor: "#051C2C",
          }),
        }),
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: brandColors.deep_blue,
        },
      },
    },
  },
});

export default theme;
