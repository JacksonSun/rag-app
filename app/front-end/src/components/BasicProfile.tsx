import { Avatar, Box, Typography } from "@mui/material";

export default function BasicProfile({
  avatar,
  name,
  bu,
  email,
}: {
  avatar: string;
  name: string;
  bu: string;
  email: string;
}) {
  return (
    <Box sx={{ display: "flex", alignItems: "center" }}>
      <Avatar src={avatar} />
      <Box>
        <Typography sx={{ mx: 2, fontWeight: 500 }}>{name}</Typography>
        <Typography sx={{ mx: 2, fontSize: 12 }}>{bu}</Typography>
        <Typography sx={{ mx: 2, fontSize: 12 }} color={"primary"}>
          {email}
        </Typography>
      </Box>
    </Box>
  );
}
