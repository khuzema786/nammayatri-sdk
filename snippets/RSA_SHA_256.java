import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openssl.PEMKeyPair;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;
import org.json.JSONObject;

import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.util.HashMap;

import javax.xml.bind.DatatypeConverter;

public class SignatureUtil {
    public static void main(String ...args) {
        JSONObject data = new JSONObject("{\"mobileNumber\":\"9819xxxx90\",\"mobileCountryCode\":\"+91\",\"merchantId\":\"NAMMA_YATRI\",\"timestamp\":\"2023-04-13T07:28:40+00:00\"}");
        String filePath = "/<absolute-path-to-folder-containing-pem-file>/private-key.pem";
        HashMap<String,String> response = createSignature(data, filePath);
    }

    public static HashMap<String,String> createSignature(JSONObject payload, String filePath) {
        try {
            PrivateKey privateKey = readPrivateKeyFromFile(filePath);
            Signature privateSignature = Signature.getInstance("SHA256withRSA");
            String[] requiredFields = {"mobileNumber", "mobileCountryCode", "merchantId", "timestamp"};
            for (String key : requiredFields)
                if(!payload.has(key))
                    throw new Exception(key + " not found in payload");
            String signatureAuthData = payload.toString();
            privateSignature.initSign(privateKey);
            privateSignature.update(signatureAuthData.getBytes(StandardCharsets.UTF_8));
            byte[] signature = privateSignature.sign();
            String encodedSignature = DatatypeConverter.printBase64Binary(signature);
            HashMap<String,String> response = new HashMap<String,String>();
            response.put("signature",encodedSignature);
            response.put("signatureAuthData", signatureAuthData);
            return response;
        } catch (Exception e) {
            e.printStackTrace();
        }
        return new HashMap<String, String>();
    }

    private static PrivateKey readPrivateKeyFromFile(String filePath) throws IOException {
        Security.addProvider(new BouncyCastleProvider());
        PEMParser pemParser = new PEMParser(new FileReader(filePath));
        JcaPEMKeyConverter converter = new JcaPEMKeyConverter().setProvider("BC");
        PEMKeyPair pemKeyPair = (PEMKeyPair) pemParser.readObject();
        KeyPair keyPair = converter.getKeyPair(pemKeyPair);
        return keyPair.getPrivate();
    }
}