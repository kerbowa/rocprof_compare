import unittest
from rocprof_compare.compare_rocprof_hsa_trace import compareRocprofHsaTrace

class TestCompareRocprofHsaTrace(unittest.TestCase):
    def testFull(self):
        expected = [
            (
                "void at::native::legacy::elementwise_kernel<128, 4, at::native::gpu_kernel_impl<at::native::FillFunctor<float> >(at::TensorIteratorBase&, at::native::FillFunctor<float> const&)::{lambda(int)#4}>(int, at::native::gpu_kernel_impl<at::native::FillFunctor<float> >(at::TensorIteratorBase&, at::native::FillFunctor<float> const&)::{lambda(int)#4}) [clone .kd]",
                640,
                4160,
                3520,
                5.5,
                3520,
                5.5,
                1,
                1,
            ),
            (
                "void at::native::modern::elementwise_kernel<at::native::FillFunctor<float>, at::detail::Array<char*, 1> >(int, at::native::FillFunctor<float>, at::detail::Array<char*, 1>) [clone .kd]",
                13440,
                15520,
                2080,
                0.15476190476190477,
                640.0,
                0.38095238095238093,
                4,
                4,
            ),
            (
                "void at::native::triu_tril_kernel<float, int, false>(at::cuda::detail::TensorInfo<float, int>, at::cuda::detail::TensorInfo<float, int>, long, long) [clone .kd]",
                26240,
                26400,
                160,
                0.006097560975609756,
                160,
                0.006097560975609756,
                1,
                1,
            ),
            (
                "void at::native::modern::elementwise_kernel<at::native::BUnaryFunctor<at::native::CompareEqFunctor<long> >, at::detail::Array<char*, 2> >(int, at::native::BUnaryFunctor<at::native::CompareEqFunctor<long> >, at::detail::Array<char*, 2>) [clone .kd]",
                7360,
                7040,
                -320,
                -0.043478260869565216,
                -320,
                -0.043478260869565216,
                1,
                1,
            ),
            (
                "void multi_tensor_apply_kernel<TensorListMetadata<4>, AdamFunctor<float>, float, float, float, float, float, float, adamMode_t, float>(int, int volatile*, TensorListMetadata<4>, AdamFunctor<float>, float, float, float, float, float, float, adamMode_t, float) [clone .kd]",
                180160,
                156640,
                -23520,
                -0.130550621669627,
                -23520,
                -0.130550621669627,
                1,
                1,
            ),
        ]
        result = compareRocprofHsaTrace('rocprof_compare/test/test_prof_data_1.csv', 'rocprof_compare/test/test_prof_data_2.csv')[0]
        print(expected)
        print(result)
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
