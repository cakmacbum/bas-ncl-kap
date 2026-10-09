import { useSession, signOut } from "./useSession";

export function AccountMenu() {
  const { session } = useSession();
  if (!session) return null;
  const user = session.user;
  const email = user.email ?? "";
  const avatar = user.user_metadata?.avatar_url as string | undefined;
  return (
    <div className="account-menu">
      {avatar ? (
        <img src={avatar} alt="" referrerPolicy="no-referrer" width={22} height={22} />
      ) : (
        <span className="account-menu__initial" aria-hidden="true">{email[0]?.toUpperCase()}</span>
      )}
      <span className="account-menu__email" title={email}>{email}</span>
      <button className="btn btn--ghost" type="button" onClick={() => void signOut()}>Sign out</button>
    </div>
  );
}
