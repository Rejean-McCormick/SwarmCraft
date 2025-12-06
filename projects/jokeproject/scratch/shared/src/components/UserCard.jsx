export default function UserCard({user}){
  return (
    <div>
      <strong>{user.name}</strong> &lt;{user.email}&gt;
    </div>
  );
}
