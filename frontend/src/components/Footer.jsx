import './Footer.css';

export default function Footer() {
    return (
        <footer className="footer">
            <div className="container">
                <p>Stocker &copy; {new Date().getFullYear()}</p>
            </div>
        </footer>
    );
}
